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
from spotseeker_server.models import Spot
import simplejson as json
from decimal import *
from django.test.utils import override_settings
from mock import patch
from django.core import cache
from spotseeker_server import models


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
class SpotSearchDistanceTest(TestCase):

    def test_invalid_latitude(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.get("/api/v1/spot", {'center_latitude': "bad_data", 'center_longitude': -40, 'distance': 10})
            self.assertEquals(response.status_code, 200, "Accepts a query with bad latitude")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            self.assertEquals(response.content, '[]', "Should return no matches")

    def test_invalid_longitude(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.get("/api/v1/spot", {'center_latitude': "30", 'center_longitude': "bad_data", 'distance': "10"})
            self.assertEquals(response.status_code, 200, "Accepts a query with bad longitude")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            self.assertEquals(response.content, '[]', "Should return no matches")

    def test_invalid_height(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.get("/api/v1/spot", {'center_latitude': "30", 'center_longitude': -40, 'height_from_sea_level': "bad_data", 'distance': "10"})
            self.assertEquals(response.status_code, 200, "Accepts a query with bad height")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            self.assertEquals(response.content, '[]', "Should return no matches")

    def test_invalid_distance(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.get("/api/v1/spot", {'center_latitude': "30", 'center_longitude': "-40", 'distance': "bad_data"})
            self.assertEquals(response.status_code, 200, "Accepts a query with bad distance")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            self.assertEquals(response.content, '[]', "Should return no matches")

    def test_large_longitude(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.get("/api/v1/spot", {'center_latitude': 30, 'center_longitude': 190, 'distance': 10})
            self.assertEquals(response.status_code, 200, "Accepts a query with too large longitude")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            self.assertEquals(response.content, '[]', "Should return no matches")

    def test_large_latitude(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.get("/api/v1/spot", {'center_latitude': 100, 'center_longitude': -40, 'distance': 10})
            self.assertEquals(response.status_code, 200, "Accepts a query with too large latitude")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            self.assertEquals(response.content, '[]', "Should return no matches")

    def test_large_negative_latitude(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.get("/api/v1/spot", {'center_latitude': -100, 'center_longitude': -40, 'distance': 10})
            self.assertEquals(response.status_code, 200, "Accepts a query with too negative latitude")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            self.assertEquals(response.content, '[]', "Should return no matches")

    def test_large_negative_longitude(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.get("/api/v1/spot", {'center_latitude': 40, 'center_longitude': -190, 'distance': 10})
            self.assertEquals(response.status_code, 200, "Accepts a query with too negative longitude")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            self.assertEquals(response.content, '[]', "Should return no matches")

    def test_no_params(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.get("/api/v1/spot", {})
            self.assertEquals(response.status_code, 200, "Accepts a query with no params")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            self.assertEquals(response.content, '[]', "Should return no matches")

    def test_distances(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):

            # Spots are in the atlantic to make them less likely to collide with actual spots
            center_lat = 30.000000
            center_long = -40.000000

            # Inner spots are 10 meters away from the center
            # Mid spots are 50 meters away from the center
            # Outer spots are 100 meters away from the center
            # Far out spots are 120 meters away, at the north

            # Creating these from the outside in, so things that sort by primary key will give bad results for things that should be sorted by distance
            for i in range(0, 100):
                far_out = Spot.objects.create(name="Far Out %s" % i, latitude=Decimal('30.0010779783'), longitude=Decimal('-40.0'))
                far_out.save()

            outer_top = Spot.objects.create(name="Outer Top", latitude=Decimal('30.0008983153'), longitude=Decimal('-40.0'))
            outer_top.save()
            outer_bottom = Spot.objects.create(name="Outer Bottom", latitude=Decimal('29.9991016847'), longitude=Decimal('-40.0'))
            outer_bottom.save()
            outer_left = Spot.objects.create(name="Outer Left", latitude=Decimal('30.0'), longitude=Decimal('-40.0010372851'))
            outer_left.save()
            outer_right = Spot.objects.create(name="Outer Right", latitude=Decimal('30.0'), longitude=Decimal('-39.9989627149'))
            outer_right.save()

            mid_top = Spot.objects.create(name="Mid Top", latitude=Decimal(' 30.0004491576'), longitude=Decimal('-40.0'))
            mid_top.save()
            mid_bottom = Spot.objects.create(name="Mid Bottom", latitude=Decimal('29.9995508424'), longitude=Decimal('-40.0'))
            mid_bottom.save()
            mid_left = Spot.objects.create(name="Mid Left", latitude=Decimal('30.0'), longitude=Decimal('-40.0005186426'))
            mid_left.save()
            mid_right = Spot.objects.create(name="Mid Right", latitude=Decimal('30.0'), longitude=Decimal('-39.9994813574'))
            mid_right.save()

            inner_top = Spot.objects.create(name="Inner Top", latitude=Decimal('30.0000898315'), longitude=Decimal('-40.0'))
            inner_top.save()
            inner_bottom = Spot.objects.create(name="Inner Bottom", latitude=Decimal('29.9999101685'), longitude=Decimal('-40.0'))
            inner_bottom.save()
            inner_left = Spot.objects.create(name="Inner Left", latitude=Decimal('30.0'), longitude=Decimal('-40.0001037285'))
            inner_left.save()
            inner_right = Spot.objects.create(name="Inner Right", latitude=Decimal('30.0'), longitude=Decimal('-39.9998962715'))
            inner_right.save()

            # Testing to make sure too small of a radius returns nothing
            c = Client()
            response = c.get("/api/v1/spot", {'center_latitude': center_lat, 'center_longitude': center_long, 'distance': 1})
            self.assertEquals(response.status_code, 200, "Accepts a query with no matches")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            self.assertEquals(response.content, '[]', "Should return no matches")

            # Testing the inner ring
            response = c.get("/api/v1/spot", {'center_latitude': center_lat, 'center_longitude': center_long, 'distance': 12})
            self.assertEquals(response.status_code, 200, "Accepts the distance query")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 4, "Returns 4 spots")
            spot_ids = {
                inner_left.pk: 1,
                inner_right.pk: 1,
                inner_top.pk: 1,
                inner_bottom.pk: 1,
            }
            for spot in spots:
                self.assertEquals(spot_ids[spot['id']], 1, "Spot matches a unique inner spot")
                spot_ids[spot['id']] = 2

            # Testing the mid ring
            response = c.get("/api/v1/spot", {'center_latitude': center_lat, 'center_longitude': center_long, 'distance': 60})
            self.assertEquals(response.status_code, 200, "Accepts the distance query")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 8, "Returns 8 spots")
            spot_ids = {
                inner_left.pk: 1,
                inner_right.pk: 1,
                inner_top.pk: 1,
                inner_bottom.pk: 1,
                mid_left.pk: 1,
                mid_right.pk: 1,
                mid_top.pk: 1,
                mid_bottom.pk: 1,
            }
            for spot in spots:
                self.assertEquals(spot_ids[spot['id']], 1, "Spot matches a unique inner or mid spot")
                spot_ids[spot['id']] = 2

            # Testing the outer ring
            response = c.get("/api/v1/spot", {'center_latitude': center_lat, 'center_longitude': center_long, 'distance': 110})
            self.assertEquals(response.status_code, 200, "Accepts the distance query")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 12, "Returns 12 spots")
            spot_ids = {
                inner_left.pk: 1,
                inner_right.pk: 1,
                inner_top.pk: 1,
                inner_bottom.pk: 1,
                mid_left.pk: 1,
                mid_right.pk: 1,
                mid_top.pk: 1,
                mid_bottom.pk: 1,
                outer_left.pk: 1,
                outer_right.pk: 1,
                outer_top.pk: 1,
                outer_bottom.pk: 1,
            }
            for spot in spots:
                self.assertEquals(spot_ids[spot['id']], 1, "Spot matches a unique inner, mid or outer spot")
                spot_ids[spot['id']] = 2

            # testing a limit - should get the inner 4, and any 2 of the mid
            response = c.get("/api/v1/spot", {'center_latitude': center_lat, 'center_longitude': center_long, 'distance': 60, 'limit': 6})
            self.assertEquals(response.status_code, 200, "Accepts the distance query")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 6, "Returns 6 spots")
            spot_ids = {
                inner_left.pk: 1,
                inner_right.pk: 1,
                inner_top.pk: 1,
                inner_bottom.pk: 1,
                mid_left.pk: 1,
                mid_right.pk: 1,
                mid_top.pk: 1,
                mid_bottom.pk: 1,
            }
            for spot in spots:
                self.assertEquals(spot_ids[spot['id']], 1, "Spot matches a unique inner, mid or outer spot")
                spot_ids[spot['id']] = 2

            self.assertEquals(spot_ids[inner_left.pk], 2, "Inner left was selected")
            self.assertEquals(spot_ids[inner_right.pk], 2, "Inner right was selected")
            self.assertEquals(spot_ids[inner_top.pk], 2, "Inner top was selected")
            self.assertEquals(spot_ids[inner_bottom.pk], 2, "Inner bottom was selected")

            # Testing limits - should get all of the inner and mid, but no outer spots
            response = c.get("/api/v1/spot", {'center_latitude': center_lat, 'center_longitude': center_long, 'distance': 101, 'limit': 8})
            self.assertEquals(response.status_code, 200, "Accepts the distance query")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 8, "Returns 8 spots")
            spot_ids = {
                inner_left.pk: 1,
                inner_right.pk: 1,
                inner_top.pk: 1,
                inner_bottom.pk: 1,
                mid_left.pk: 1,
                mid_right.pk: 1,
                mid_top.pk: 1,
                mid_bottom.pk: 1,
            }
            for spot in spots:
                self.assertEquals(spot_ids[spot['id']], 1, "Spot matches a unique inner or mid spot")
                spot_ids[spot['id']] = 2

            # Testing limits - should get all inner and mid spots, and 2 outer spots
            response = c.get("/api/v1/spot", {'center_latitude': center_lat, 'center_longitude': center_long, 'distance': 101, 'limit': 10})
            self.assertEquals(response.status_code, 200, "Accepts the distance query")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 10, "Returns 10 spots")
            spot_ids = {
                inner_left.pk: 1,
                inner_right.pk: 1,
                inner_top.pk: 1,
                inner_bottom.pk: 1,
                mid_left.pk: 1,
                mid_right.pk: 1,
                mid_top.pk: 1,
                mid_bottom.pk: 1,
                outer_left.pk: 1,
                outer_right.pk: 1,
                outer_top.pk: 1,
                outer_bottom.pk: 1,
            }
            for spot in spots:
                self.assertEquals(spot_ids[spot['id']], 1, "Spot matches a unique inner, mid or outer spot")
                spot_ids[spot['id']] = 2

            self.assertEquals(spot_ids[inner_left.pk], 2, "Inner left was selected")
            self.assertEquals(spot_ids[inner_right.pk], 2, "Inner right was selected")
            self.assertEquals(spot_ids[inner_top.pk], 2, "Inner top was selected")
            self.assertEquals(spot_ids[inner_bottom.pk], 2, "Inner bottom was selected")

            self.assertEquals(spot_ids[mid_left.pk], 2, "Mid left was selected")
            self.assertEquals(spot_ids[mid_right.pk], 2, "Mid rightwas selected")
            self.assertEquals(spot_ids[mid_top.pk], 2, "Mid top was selected")
            self.assertEquals(spot_ids[mid_bottom.pk], 2, "Mid bottom was selected")

            # Testing that limit 0 = no limit - get all 12 spots
            response = c.get("/api/v1/spot", {'center_latitude': center_lat, 'center_longitude': center_long, 'distance': 110, 'limit': 0})
            self.assertEquals(response.status_code, 200, "Accepts the distance query")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 12, "Returns 12 spots with a limit of 0")
            spot_ids = {
                inner_left.pk: 1,
                inner_right.pk: 1,
                inner_top.pk: 1,
                inner_bottom.pk: 1,
                mid_left.pk: 1,
                mid_right.pk: 1,
                mid_top.pk: 1,
                mid_bottom.pk: 1,
                outer_left.pk: 1,
                outer_right.pk: 1,
                outer_top.pk: 1,
                outer_bottom.pk: 1,
            }
            for spot in spots:
                self.assertEquals(spot_ids[spot['id']], 1, "Spot matches a unique inner, mid or outer spot")
                spot_ids[spot['id']] = 2

            # Testing that the default limit is 20 spaces
            response = c.get("/api/v1/spot", {'center_latitude': center_lat, 'center_longitude': center_long, 'distance': 150})
            self.assertEquals(response.status_code, 200, "Accepts the distance query")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 20, "Returns 20 spots with no defined limit")
            spot_ids = {
                inner_left.pk: 1,
                inner_right.pk: 1,
                inner_top.pk: 1,
                inner_bottom.pk: 1,
                mid_left.pk: 1,
                mid_right.pk: 1,
                mid_top.pk: 1,
                mid_bottom.pk: 1,
                outer_left.pk: 1,
                outer_right.pk: 1,
                outer_top.pk: 1,
                outer_bottom.pk: 1,
            }

            far_out_count = 0
            for spot in spots:
                if spot['id'] in spot_ids:
                    self.assertEquals(spot_ids[spot['id']], 1, "Spot matches a unique inner, mid or outer spot")
                else:
                    far_out_count += 1

            self.assertEquals(far_out_count, 8, "Found 8 far out spots to fill in the limit of 20")

            # Testing that with a limit of 0, we pull in all spots in range
            response = c.get("/api/v1/spot", {'center_latitude': center_lat, 'center_longitude': center_long, 'distance': 130, 'limit': 0})
            self.assertEquals(response.status_code, 200, "Accepts the distance query")
            self.assertEquals(response["Content-Type"], "application/json", "Has the json header")
            spots = json.loads(response.content)
            self.assertEquals(len(spots), 112, "Returns 112 spots with a limit of 0")
            spot_ids = {
                inner_left.pk: 1,
                inner_right.pk: 1,
                inner_top.pk: 1,
                inner_bottom.pk: 1,
                mid_left.pk: 1,
                mid_right.pk: 1,
                mid_top.pk: 1,
                mid_bottom.pk: 1,
                outer_left.pk: 1,
                outer_right.pk: 1,
                outer_top.pk: 1,
                outer_bottom.pk: 1,
            }

            far_out_count = 0
            for spot in spots:
                if spot['id'] in spot_ids:
                    self.assertEquals(spot_ids[spot['id']], 1, "Spot matches a unique inner, mid or outer spot")
                else:
                    far_out_count += 1

            self.assertEquals(far_out_count, 100, "Found all 100 far out spots")
