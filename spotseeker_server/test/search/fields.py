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
from spotseeker_server import models
from spotseeker_server.cache import memory_cache


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
class SpotSearchFieldTest(TestCase):

    def setUp(self):
        self.spot1 = Spot.objects.create(name="This is a \
                                    searchable Name - OUGL")
        self.spot1.save()

        self.spot2 = Spot.objects.create(name="This OUGL \
                                    is an alternative spot")
        self.spot2.save()

        self.spot3 = Spot.objects.create(name="3rd spot")
        self.spot3.save()

        self.spot4 = Spot.objects.create(name="OUGL  - 3rd spot in the site")
        self.spot4.save()

        self.spot5 = Spot.objects.create(name="Has whiteboards")
        attr = SpotExtendedInfo(key="has_whiteboards",
                                value=True, spot=self.spot5)
        attr.save()
        self.spot5.save()

        self.spot6 = Spot.objects.create(name="Has no whiteboards")
        attr = SpotExtendedInfo(key="has_whiteboards",
                                value=False, spot=self.spot6)
        attr.save()
        self.spot6.save()

        self.spot7 = Spot.objects.create(
            name="Text search for the title - Odegaard Undergraduate \
            Library and Learning Commons"
        )
        attr = SpotExtendedInfo(key="has_whiteboards",
                                value=True, spot=self.spot7)
        attr.save()
        self.spot7.save()

        self.natural = Spot.objects.create(name="Has field value: natural")
        attr = SpotExtendedInfo(key="lightingmultifieldtest",
                                value="natural", spot=self.natural)
        attr.save()
        self.natural.save()

        self.artificial = Spot.objects.create(
            name="Has field value: artificial")
        attr = SpotExtendedInfo(key="lightingmultifieldtest",
                                value="artificial", spot=self.artificial)
        attr.save()
        self.artificial.save()

        self.other = Spot.objects.create(name="Has field value: other")
        attr = SpotExtendedInfo(key="lightingmultifieldtest",
                                value="other", spot=self.other)
        attr.save()
        self.other.save()

        self.darkness = Spot.objects.create(name="Has field value: darkness")
        self.darkness.save()

        self.american_food_spot = Spot.objects.create(name='American Food')
        ei1 = SpotExtendedInfo.objects.create(key='s_cuisine_american',
                                              value='true',
                                              spot=self.american_food_spot)
        ei1.save()
        at1 = SpotExtendedInfo.objects.create(key='app_type',
                                              value='food',
                                              spot=self.american_food_spot)
        at1.save()
        attr = SpotExtendedInfo.objects.create(key='s_payment_husky',
                                               value='true',
                                               spot=self.american_food_spot)
        attr.save()
        self.american_food_spot.save()

        self.bbq_food_spot = Spot.objects.create(name='BBQ')
        ei2 = SpotExtendedInfo.objects.create(key='s_cuisine_bbq',
                                              value='true',
                                              spot=self.bbq_food_spot)
        ei2.save()
        attr = SpotExtendedInfo.objects.create(key='s_payment_cash',
                                               value='true',
                                               spot=self.bbq_food_spot)
        attr.save()
        at2 = SpotExtendedInfo.objects.create(key='app_type',
                                              value='food',
                                              spot=self.bbq_food_spot)
        at2.save()
        self.bbq_food_spot.save()

        self.food_court_spot = Spot.objects.create(name='Food Court')
        ei3 = SpotExtendedInfo.objects.create(key='s_cuisine_american',
                                              value='true',
                                              spot=self.food_court_spot)
        ei3.save()
        ei4 = SpotExtendedInfo.objects.create(key='s_cuisine_bbq',
                                              value='true',
                                              spot=self.food_court_spot)
        ei4.save()
        at3 = SpotExtendedInfo.objects.create(key='app_type',
                                              value='food',
                                              spot=self.food_court_spot)
        at3.save()
        attr = SpotExtendedInfo.objects.create(key='s_payment_husky',
                                               value='true',
                                               spot=self.food_court_spot)
        attr.save()
        attr = SpotExtendedInfo.objects.create(key='s_payment_cash',
                                               value='true',
                                               spot=self.food_court_spot)
        attr.save()
        self.food_court_spot.save()

        self.chinese_food_spot = Spot.objects.create(name='Chinese Food')
        ei5 = SpotExtendedInfo.objects.create(key='s_cuisine_chinese',
                                              value='true',
                                              spot=self.chinese_food_spot)
        ei5.save()
        at4 = SpotExtendedInfo.objects.create(key='app_type',
                                              value='food',
                                              spot=self.chinese_food_spot)
        at4.save()
        att = SpotExtendedInfo.objects.create(key='s_payment_cash',
                                              value='true',
                                              spot=self.chinese_food_spot)
        attr.save()
        self.chinese_food_spot.save()

        self.study_spot = Spot.objects.create(name='Study Here!')
        ei6 = SpotExtendedInfo.objects.create(key='has_whiteboards',
                                              value='true',
                                              spot=self.study_spot)
        ei6.save()
        self.study_spot.save()

        cafe_type = SpotType.objects.get_or_create(name='cafe_testing')[0]
        open_type = SpotType.objects.get_or_create(name='open_testing')[0]
        never_used_type = SpotType.objects.get_or_create(
            name='never_used_testing')[0]

        self.spot8 = Spot.objects.create(name='Spot8 is a Cafe for \
                                    multi type test')
        self.spot8.spottypes.add(cafe_type)
        self.spot8.save()

        self.spot9 = Spot.objects.create(name='Spot 9 is an Open space for \
                                    multi type test')
        self.spot9.spottypes.add(open_type)
        self.spot9.save()

        self.spot10 = Spot.objects.create(name='Spot 10 is an Open cafe for \
                                    multi type test')
        self.spot10.spottypes.add(cafe_type)
        self.spot10.spottypes.add(open_type)
        self.spot10.save()

        self.spot11 = Spot.objects.create(name='Spot 11 should never \
                                          get returned')
        self.spot11.spottypes.add(never_used_type)
        self.spot11.save()

        self.spot12 = Spot.objects.create(name='Room A403',
                                          building_name='Building A')
        self.spot12.save()

        self.spot13 = Spot.objects.create(name='Room A589',
                                          building_name='Building A')
        self.spot13.save()

        self.spot14 = Spot.objects.create(name='Room B328',
                                          building_name='Building B')
        self.spot14.save()

        self.spot15 = Spot.objects.create(name='Room B943',
                                          building_name='Building B')
        self.spot15.save()

        self.spot16 = Spot.objects.create(name='Room C483',
                                          building_name='Building C')
        self.spot16.save()

        self.client = Client()

    def tearDown(self):
        memory_cache.clear_cache()

    def test_fields(self):
        response = self.client.get("/api/v1/spot", {'name': 'OUGL'})

        spot_ids = {
            self.spot1.pk: 1,
            self.spot2.pk: 1,
            self.spot4.pk: 1,
        }

        self.assertEqual(response.status_code, 200, "Accepts name query")
        self.assertEqual(response["Content-Type"],
                         "application/json",
                         "Has the json header")
        spots = json.loads(response.content)
        self.assertEqual(len(spots), 3, 'Find 3 matches for OUGL')

        for spot in spots:
            self.assertEqual(spot_ids[spot['id']], 1,
                             "Includes each spot, uniquely")
            spot_ids[spot['id']] = 2

        response = self.client.get(
            "/api/v1/spot",
            {'extended_info:has_whiteboards': True}
        )
        self.assertEqual(response.status_code, 200,
                         "Accepts whiteboards query")
        self.assertEqual(response["Content-Type"],
                         "application/json",
                         "Has the json header")
        spots = json.loads(response.content)
        self.assertEqual(len(spots), 2)

        self.assertEqual(spots[0]['id'], self.spot5.pk,
                         "Finds spot5 w/ a whiteboard")

        response = self.client.get(
            "/api/v1/spot",
            {'extended_info:has_whiteboards': True,
             'name': 'odegaard under'}
        )
        self.assertEqual(
            response.status_code,
            200,
            "Accepts whiteboards + name query")
        self.assertEqual(
            response["Content-Type"],
            "application/json",
            "Has the json header")
        spots = json.loads(response.content)
        self.assertEqual(len(spots), 1,
                         'Finds 1 match for whiteboards + odegaard')

        self.assertEqual(spots[0]['id'],
                         self.spot7.pk,
                         "Finds spot7 w/ a whiteboard + odegaard")

    def test_invalid_field(self):
        response = self.client.get("/api/v1/spot",
                                   {'invalid_field': 'OUGL'})
        self.assertEqual(response.status_code, 200,
                         "Accepts an invalid field in query")
        self.assertEqual(response["Content-Type"],
                         "application/json", "Has the json header")
        self.assertEqual(response.content, '[]',
                         "Should return no matches")

    def test_invalid_extended_info(self):
        response = self.client.get(
            "/api/v1/spot",
            {'extended_info:invalid_field': 'OUGL'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"],
                         "application/json",
                         "Has the json header")
        self.assertEqual(response.content,
                         '[]',
                         "Should return no matches")

    def test_multi_value_field(self):
        response = self.client.get(
            "/api/v1/spot",
            {'extended_info:lightingmultifieldtest': 'natural'}
        )
        self.assertEquals(
            response["Content-Type"],
            "application/json",
            "Has the json header"
        )
        spots = json.loads(response.content)
        self.assertEquals(
            len(spots),
            1,
            'Finds 1 match for lightingmultifieldtest - natural'
        )
        self.assertEquals(
            spots[0]['id'],
            self.natural.pk,
            "Finds natural light spot"
        )

        response = self.client.get(
            "/api/v1/spot",
            {'extended_info:lightingmultifieldtest': 'artificial'}
        )
        self.assertEqual(
            response["Content-Type"],
            "application/json",
            "Has the json header"
        )
        spots = json.loads(response.content)
        self.assertEqual(
            len(spots),
            1,
            'Finds 1 match for lightingmultifieldtest - artificial'
        )
        self.assertEqual(spots[0]['id'],
                         self.artificial.pk,
                         "Finds artificial light spot")

        response = self.client.get(
            "/api/v1/spot",
            {'extended_info:lightingmultifieldtest': 'other'}
        )
        self.assertEqual(
            response["Content-Type"],
            "application/json",
            "Has the json header"
        )
        spots = json.loads(response.content)
        self.assertEqual(
            len(spots),
            1,
            'Finds 1 match for lightingmultifieldtest - other'
        )
        self.assertEqual(spots[0]['id'],
                         self.other.pk,
                         "Finds other light spot")

        response = self.client.get(
            "/api/v1/spot",
            {'extended_info:lightingmultifieldtest': ('other', 'natural')}
        )
        self.assertEqual(
            response["Content-Type"],
            "application/json",
            "Has the json header"
        )
        spots = json.loads(response.content)
        self.assertEqual(
            len(spots),
            2,
            'Finds 2 match for lightingmultifieldtest - other + natural'
        )

        spot_ids = {
            self.other.pk: 1,
            self.natural.pk: 1,
        }

        for spot in spots:
            self.assertEqual(
                spot_ids[spot['id']],
                1,
                "Includes each spot, uniquely"
            )
            spot_ids[spot['id']] = 2

        # For this next test, make sure
        # we're trying to get spots that actually exist.
        ids = (Spot.objects.all()[0].id,
               Spot.objects.all()[1].id,
               Spot.objects.all()[2].id,
               Spot.objects.all()[3].id,)

        response = self.client.get("/api/v1/spot", {'id': ids})
        self.assertEqual(
            response["Content-Type"],
            "application/json",
            "Has the json header"
        )
        spots = json.loads(response.content)
        self.assertEqual(
            len(spots),
            4,
            'Finds 4 matches for searching for 4 ids'
            )
        spot_ids[spot['id']] = 2

    def test_extended_info_or(self):
        """ Tests searches for Spots with
        extended_info that has multiple values. """
        response = self.client.get(
            "/api/v1/spot",
            {'extended_info:or:s_cuisine_bbq': 'true',
             'extended_info:or:s_cuisine_american': 'true',
             'extended_info:app_type': 'food'}
        )
        self.assertEqual(response.status_code, 200)
        spots = json.loads(response.content)
        self.assertEqual(len(spots), 3)
        self.assertTrue(
            self.american_food_spot.json_data_structure() in spots
        )
        self.assertTrue(
            self.bbq_food_spot.json_data_structure() in spots
        )
        self.assertTrue(
            self.food_court_spot.json_data_structure() in spots
        )
        self.assertTrue(
            self.chinese_food_spot.json_data_structure() not in spots
        )
        self.assertTrue(
            self.study_spot.json_data_structure() not in spots
        )

    def test_multi_type_spot(self):
        response = self.client.get("/api/v1/spot",
                                   {"type": "cafe_testing"})
        self.assertEqual(
            response["Content-Type"],
            "application/json",
            "Has the json header"
        )
        spots = json.loads(response.content)
        self.assertEqual(
            len(spots),
            2,
            'Finds 2 matches for searching for type cafe_test'
        )

        response = self.client.get("/api/v1/spot",
                                   {"type": "open_testing"})
        self.assertEqual(
            response["Content-Type"],
            "application/json",
            "Has the json header"
        )
        spots = json.loads(response.content)
        self.assertEqual(
            len(spots),
            2,
            'Finds 2 matches for searching for type open_test'
        )

        response = self.client.get(
            "/api/v1/spot",
            {"type": ["cafe_testing", "open_testing"]}
        )
        self.assertEqual(
            response["Content-Type"],
            "application/json",
            "Has the json header"
        )
        spots = json.loads(response.content)
        self.assertEqual(
            len(spots),
            3,
            'Finds 3 matches for searching for cafe_test and open_test'
        )

    def test_multi_building_search(self):
        """ Tests to be sure searching for spots in
        multiple buildings returns spots for all buildings.
        """
        response = self.client.get("/api/v1/spot",
                                   {"building_name": ['Building A',
                                                      'Building B']})
        spots = json.loads(response.content)

        response_ids = []
        for s in spots:
            response_ids.append(s['id'])

        self.assertTrue(self.spot12.pk in response_ids,
                        'Spot 12 is returned')
        self.assertTrue(self.spot13.pk in response_ids,
                        'Spot 13 is returned')
        self.assertTrue(self.spot14.pk in response_ids,
                        'Spot 14 is returned')
        self.assertTrue(self.spot15.pk in response_ids,
                        'Spot 15 is returned')
        self.assertTrue(self.spot16.pk not in response_ids,
                        'Spot 16 is not returned')
        self.assertEqual(
            len(spots),
            4,
            'Finds 4 matches searching for spots in Buildings A and B'
        )

    def test_extended_info_or_gouping(self):
        """ Tests searches for Spots with
        extended_info that has multiple values. """
        response = self.client.get(
            "/api/v1/spot",
            {'extended_info:app_type': 'food',
             'extended_info:or_group:cuisine': ['s_cuisine_bbq',
                                                's_cuisine_american']}
        )
        self.assertEqual(response.status_code, 200)
        spots = json.loads(response.content)
        self.assertEqual(len(spots), 3)
        self.assertTrue(
            self.american_food_spot.json_data_structure() in spots
        )
        self.assertTrue(
            self.bbq_food_spot.json_data_structure() in spots
        )
        self.assertTrue(
            self.food_court_spot.json_data_structure() in spots
        )
        self.assertTrue(
            self.chinese_food_spot.json_data_structure() not in spots
        )
        self.assertTrue(
            self.study_spot.json_data_structure() not in spots
        )

    def test_extended_info_or_gouping_many(self):
        """ Tests searches for Spots with
        extended_info that has multiple values. """
        response = self.client.get(
            "/api/v1/spot",
            {'extended_info:app_type': 'food',
             'extended_info:or_group:groupone': ['s_cuisine_bbq',
                                                 's_cuisine_american'],
             'extended_info:or_group:grouptwo': ['s_payment_husky',
                                                 's_payment_cash']}
        )
        self.assertEqual(response.status_code, 200)
        spots = json.loads(response.content)
        self.assertEqual(len(spots), 3)
        self.assertTrue(
            self.american_food_spot.json_data_structure() in spots
        )
        self.assertTrue(
            self.bbq_food_spot.json_data_structure() in spots
        )
        self.assertTrue(
            self.food_court_spot.json_data_structure() in spots
        )
        self.assertTrue(
            self.chinese_food_spot.json_data_structure() not in spots
        )
        self.assertTrue(
            self.study_spot.json_data_structure() not in spots
        )
