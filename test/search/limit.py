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
from django.test.client import Client
from spotseeker_server.models import Spot
import simplejson as json
from django.test.utils import override_settings
from mock import patch
from django.core import cache
from spotseeker_server import models


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
class SpotSearchLimitTest(TestCase):
    def setUp(self):
        num_spots = 25
        self.num_spots = num_spots
        for i in range(num_spots):
            i = i + 1
            Spot.objects.create(name="spot %s" % (i))

    def test_more_than_20_no_limit(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            get_request = "/api/v1/spot?"
            num_spots = self.num_spots

            for i in range(num_spots):
                i = i + 1
                get_request = get_request + "id=%s&" % (i)

            response = c.get(get_request)
            self.assertEquals(response.status_code, 400, "400 is thrown if more than 20 spots are requested without a limit")

    def test_less_than_20_no_limit(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            get_request = "/api/v1/spot?"
            num_spots = self.num_spots - 10

            for i in range(num_spots):
                i = i + 1
                get_request = get_request + "id=%s&" % (i)

            response = c.get(get_request)
            spots = json.loads(response.content)
            self.assertEquals(len(spots), num_spots, "Spots requested were returned if less than 20 spots are requested without a limit")

    def test_more_than_20_with_limit(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            get_request = "/api/v1/spot?"
            num_spots = self.num_spots

            for i in range(num_spots):
                i = i + 1
                get_request = get_request + "id=%s&" % (i)
            get_request = get_request + "limit=%d" % (num_spots)

            response = c.get(get_request)
            spots = json.loads(response.content)
            self.assertEquals(len(spots), num_spots, "Spots requested were returned even though more than 20 because a limit was included")
