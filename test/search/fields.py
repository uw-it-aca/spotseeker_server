""" Copyright 2012, 2013 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot, SpotExtendedInfo, SpotType
import simplejson as json
from django.test.utils import override_settings
from mock import patch
from django.core import cache
from spotseeker_server import models


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
class SpotSearchFieldTest(TestCase):

    def test_fields(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            spot1 = Spot.objects.create(name="This is a searchable Name - OUGL")
            spot1.save()

            spot2 = Spot.objects.create(name="This OUGL is an alternative spot")
            spot2.save()

            spot3 = Spot.objects.create(name="3rd spot")
            spot3.save()

            spot4 = Spot.objects.create(name="OUGL  - 3rd spot in the site")
            spot4.save()

            c = Client()
            response = c.get("/api/v1/spot", {'name': 'OUGL'})
            self.assertEquals(response.status_code, 200, "Accepts name query")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 3, 'Find 3 matches for OUGL')

            spot_ids = {
                spot1.pk: 1,
                spot2.pk: 1,
                spot4.pk: 1,
            }

            for spot in spots:
                self.assertEquals(spot_ids[spot['id']], 1, "Includes each spot, uniquely")
                spot_ids[spot['id']] = 2

            # This part is essentially imagination...
            spot5 = Spot.objects.create(name="Has whiteboards")
            attr = SpotExtendedInfo(key="has_whiteboards", value=True, spot=spot5)
            attr.save()
            spot5.save()

            spot6 = Spot.objects.create(name="Has no whiteboards")
            attr = SpotExtendedInfo(key="has_whiteboards", value=False, spot=spot6)
            attr.save()
            spot6.save()

            response = c.get("/api/v1/spot", {'extended_info:has_whiteboards': True})
            self.assertEquals(response.status_code, 200, "Accepts whiteboards query")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 1, 'Finds 1 match for whiteboards')

            self.assertEquals(spots[0]['id'], spot5.pk, "Finds spot5 w/ a whiteboard")

            spot7 = Spot.objects.create(name="Text search for the title - Odegaard Undergraduate Library and Learning Commons")
            attr = SpotExtendedInfo(key="has_whiteboards", value=True, spot=spot7)
            attr.save()
            spot7.save()

            response = c.get("/api/v1/spot", {'extended_info:has_whiteboards': True, 'name': 'odegaard under'})
            self.assertEquals(response.status_code, 200, "Accepts whiteboards + name query")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 1, 'Finds 1 match for whiteboards + odegaard')

            self.assertEquals(spots[0]['id'], spot7.pk, "Finds spot7 w/ a whiteboard + odegaard")

    def test_invalid_field(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.get("/api/v1/spot", {'invalid_field': 'OUGL'})
            self.assertEquals(response.status_code, 200, "Accepts an invalid field in query")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            self.assertEquals(response.content, '[]', "Should return no matches")

    def test_invalid_extended_info(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.get("/api/v1/spot", {'extended_info:invalid_field': 'OUGL'})
            self.assertEquals(response.status_code, 200, "Accepts an invalid extended_info field in query")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            self.assertEquals(response.content, '[]', "Should return no matches")

    def test_multi_value_field(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            natural = Spot.objects.create(name="Has field value: natural")
            attr = SpotExtendedInfo(key="lightingmultifieldtest", value="natural", spot=natural)
            attr.save()

            artificial = Spot.objects.create(name="Has field value: artificial")
            attr = SpotExtendedInfo(key="lightingmultifieldtest", value="artificial", spot=artificial)
            attr.save()

            other = Spot.objects.create(name="Has field value: other")
            attr = SpotExtendedInfo(key="lightingmultifieldtest", value="other", spot=other)
            attr.save()

            darkness = Spot.objects.create(name="Has field value: darkness")

            c = Client()
            response = c.get("/api/v1/spot", {'extended_info:lightingmultifieldtest': 'natural'})
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 1, 'Finds 1 match for lightingmultifieldtest - natural')
            self.assertEquals(spots[0]['id'], natural.pk, "Finds natural light spot")

            response = c.get("/api/v1/spot", {'extended_info:lightingmultifieldtest': 'artificial'})
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 1, 'Finds 1 match for lightingmultifieldtest - artificial')
            self.assertEquals(spots[0]['id'], artificial.pk, "Finds artificial light spot")

            response = c.get("/api/v1/spot", {'extended_info:lightingmultifieldtest': 'other'})
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 1, 'Finds 1 match for lightingmultifieldtest - other')
            self.assertEquals(spots[0]['id'], other.pk, "Finds other light spot")

            response = c.get("/api/v1/spot", {'extended_info:lightingmultifieldtest': ('other', 'natural')})
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 2, 'Finds 2 match for lightingmultifieldtest - other + natural')

            spot_ids = {
                other.pk: 1,
                natural.pk: 1,
            }

            for spot in spots:
                self.assertEquals(spot_ids[spot['id']], 1, "Includes each spot, uniquely")
                spot_ids[spot['id']] = 2

            # For this next test, make sure we're trying to get spots that actually exist.
            ids = (Spot.objects.all()[0].id,
                   Spot.objects.all()[1].id,
                   Spot.objects.all()[2].id,
                   Spot.objects.all()[3].id,)

            response = c.get("/api/v1/spot", {'id': ids})
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 4, 'Finds 4 matches for searching for 4 ids')

    def test_multi_type_spot(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            cafe_type = SpotType.objects.get_or_create(name='cafe_testing')[0]  # Index 0 because get_or_create returns a Tuple of value and T/F if it was created
            open_type = SpotType.objects.get_or_create(name='open_testing')[0]
            never_used_type = SpotType.objects.get_or_create(name='never_used_testing')[0]

            spot1 = Spot.objects.create(name='Spot1 is a Cafe for multi type test')
            spot1.spottypes.add(cafe_type)
            spot1.save()
            spot2 = Spot.objects.create(name='Spot 2 is an Open space for multi type test')
            spot2.spottypes.add(open_type)
            spot2.save()
            spot3 = Spot.objects.create(name='Spot 3 is an Open cafe for multi type test')
            spot3.spottypes.add(cafe_type)
            spot3.spottypes.add(open_type)
            spot3.save()
            spot4 = Spot.objects.create(name='Spot 4 should never get returned')
            spot4.spottypes.add(never_used_type)
            spot4.save()

            response = c.get("/api/v1/spot", {"type": "cafe_testing"})
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 2, 'Finds 2 matches for searching for type cafe_test')

            response = c.get("/api/v1/spot", {"type": "open_testing"})
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 2, 'Finds 2 matches for searching for type open_test')

            response = c.get("/api/v1/spot", {"type": ["cafe_testing", "open_testing"]})
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 3, 'Finds 3 matches for searching for cafe_test and open_test')

    def test_multi_building_search(self):
        """ Tests to be sure searching for spots in multiple buildings returns spots for all buildings.
        """
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            # Building A
            spot1 = Spot.objects.create(name='Room A403', building_name='Building A')
            spot2 = Spot.objects.create(name='Room A589', building_name='Building A')

            # Building B
            spot3 = Spot.objects.create(name='Room B328', building_name='Building B')
            spot4 = Spot.objects.create(name='Room B943', building_name='Building B')

            # Building C - just because
            spot5 = Spot.objects.create(name='Room C483', building_name='Building C')

            c = Client()
            response = c.get("/api/v1/spot", {"building_name": ['Building A', 'Building B']})
            spots = json.loads(response.content)

            response_ids = []
            for s in spots:
                response_ids.append(s['id'])

            self.assertTrue(spot1.pk in response_ids, 'Spot 1 is returned')
            self.assertTrue(spot2.pk in response_ids, 'Spot 2 is returned')
            self.assertTrue(spot3.pk in response_ids, 'Spot 3 is returned')
            self.assertTrue(spot4.pk in response_ids, 'Spot 4 is returned')
            self.assertTrue(spot5.pk not in response_ids, 'Spot 5 is not returned')
            self.assertEquals(len(spots), 4, 'Finds 4 matches searching for spots in Buildings A and B')

    # This unit test is currently invalid, as of dbdb3def8046a4f52e5bb23194423e913397e92f - if we decide duplicate keys should be allowed again, this may become valid.
    #def test_duplicate_extended_info(self):
    #    dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
    #    with patch.object(models, 'cache', dummy_cache):
    #        with self.settings(SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm'):
    #            spot = Spot.objects.create(name="This is for testing GET", latitude=55, longitude=30)
    #            spot.save()
    #            self.spot = spot

    #            c = Client()
    #            SpotExtendedInfo.objects.create(key='has_soda_fountain', value='true', spot=spot)
    #            SpotExtendedInfo.objects.create(key='has_soda_fountain', value='true', spot=spot)
    #            response = c.get("/api/v1/spot", {"center_latitude": 55.1, "center_longitude": 30.1, "distance": 100000, "extended_info:has_soda_fountain": "true"})
    #            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
    #            spots = json.loads(response.content)
    #            self.assertEquals(len(spots), 1, 'Finds 1 match searching on has_soda_fountain=true')
