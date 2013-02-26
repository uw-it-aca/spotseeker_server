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
class SpotSearchCapacityTest(TestCase):
    def test_capacity(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            spot1 = Spot.objects.create(name="capacity: 1", capacity=1)
            spot1.save()

            spot2 = Spot.objects.create(name="capacity: 2", capacity=2)
            spot2.save()

            spot3 = Spot.objects.create(name="capacity: 3", capacity=3)
            spot3.save()

            spot4 = Spot.objects.create(name="capacity: 4", capacity=4)
            spot4.save()

            spot5 = Spot.objects.create(name="capacity: 50", capacity=50)
            spot5.save()

            c = Client()
            response = c.get("/api/v1/spot", {'capacity': '', 'name': 'capacity'})
            spots = json.loads(response.content)

            has_1 = False
            has_2 = False
            has_3 = False
            has_4 = False
            has_5 = False

            for spot in spots:
                if spot['id'] == spot1.pk:
                    has_1 = True
                if spot['id'] == spot2.pk:
                    has_2 = True
                if spot['id'] == spot3.pk:
                    has_3 = True
                if spot['id'] == spot4.pk:
                    has_4 = True
                if spot['id'] == spot5.pk:
                    has_5 = True

            self.assertEquals(has_1, True)
            self.assertEquals(has_2, True)
            self.assertEquals(has_3, True)
            self.assertEquals(has_4, True)
            self.assertEquals(has_5, True)

            response = c.get("/api/v1/spot", {'capacity': '1'})
            spots = json.loads(response.content)

            has_1 = False
            has_2 = False
            has_3 = False
            has_4 = False
            has_5 = False

            for spot in spots:
                if spot['id'] == spot1.pk:
                    has_1 = True
                if spot['id'] == spot2.pk:
                    has_2 = True
                if spot['id'] == spot3.pk:
                    has_3 = True
                if spot['id'] == spot4.pk:
                    has_4 = True
                if spot['id'] == spot5.pk:
                    has_5 = True

            self.assertEquals(has_1, True)
            self.assertEquals(has_2, True)
            self.assertEquals(has_3, True)
            self.assertEquals(has_4, True)
            self.assertEquals(has_5, True)

            response = c.get("/api/v1/spot", {'capacity': '49'})
            spots = json.loads(response.content)

            has_1 = False
            has_2 = False
            has_3 = False
            has_4 = False
            has_5 = False

            for spot in spots:
                if spot['id'] == spot1.pk:
                    has_1 = True
                if spot['id'] == spot2.pk:
                    has_2 = True
                if spot['id'] == spot3.pk:
                    has_3 = True
                if spot['id'] == spot4.pk:
                    has_4 = True
                if spot['id'] == spot5.pk:
                    has_5 = True

            self.assertEquals(has_1, False)
            self.assertEquals(has_2, False)
            self.assertEquals(has_3, False)
            self.assertEquals(has_4, False)
            self.assertEquals(has_5, True)

            response = c.get("/api/v1/spot", {'capacity': '501'})
            spots = json.loads(response.content)

            has_1 = False
            has_2 = False
            has_3 = False
            has_4 = False
            has_5 = False

            for spot in spots:
                if spot['id'] == spot1.pk:
                    has_1 = True
                if spot['id'] == spot2.pk:
                    has_2 = True
                if spot['id'] == spot3.pk:
                    has_3 = True
                if spot['id'] == spot4.pk:
                    has_4 = True
                if spot['id'] == spot5.pk:
                    has_5 = True

            self.assertEquals(has_1, False)
            self.assertEquals(has_2, False)
            self.assertEquals(has_3, False)
            self.assertEquals(has_4, False)
            self.assertEquals(has_5, False)

            response = c.get("/api/v1/spot", {'capacity': '1', 'limit': '4'})
            #testing sorting by distance, which is impossible given no center
            self.assertEquals(response.status_code, 400)
