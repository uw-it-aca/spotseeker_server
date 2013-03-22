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
import random
from django.test.utils import override_settings
from mock import patch
from django.core import cache
from spotseeker_server import models


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                   SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm')
class SpotPOSTTest(TestCase):
    """ Tests creating a new Spot via POST.
    """

    def test_valid_json(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            response = c.post('/api/v1/spot/', '{"name":"%s","capacity":"%d", "location": {"latitude": 50, "longitude": -30} }' % (new_name, new_capacity), content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")
            self.assertIn("Location", response, "The response has a location header")

            self.spot = Spot.objects.get(name=new_name)

            self.assertEquals(response["Location"], 'http://testserver' + self.spot.rest_url(), "The uri for the new spot is correct")

            get_response = c.get(response["Location"])
            self.assertEquals(get_response.status_code, 200, "OK in response to GETing the new spot")

            spot_json = json.loads(get_response.content)

            self.assertEquals(spot_json["name"], new_name, "The right name was stored")
            self.assertEquals(spot_json["capacity"], new_capacity, "The right capacity was stored")

    def test_non_json(self):
        c = Client()
        response = c.post('/api/v1/spot/', 'just a string', content_type="application/json", follow=False)
        self.assertEquals(response.status_code, 400)

    def test_invalid_json(self):
        c = Client()
        response = c.post('/api/v1/spot/', '{}', content_type="application/json", follow=False)
        self.assertEquals(response.status_code, 400)

    def test_extended_info(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            json_string = '{"name":"%s","capacity":"%s", "location": {"latitude": 50, "longitude": -30},"extended_info":{"has_outlets":"true"}}' % (new_name, new_capacity)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)
            get_response = c.get(response["Location"])
            spot_json = json.loads(get_response.content)
            extended_info = {"has_outlets": "true"}
            self.assertEquals(spot_json["extended_info"], extended_info, "extended_info was succesffuly POSTed")

    def test_multiple_correct_extended_info(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            json_string1 = '{"name":"%s","capacity":"10", "location": {"latitude": 50, "longitude": -30},"extended_info":{"has_whiteboards":"true", "has_printing":"true", "has_displays":"true", "num_computers":"38", "has_natural_light":"true"}}' % ("testing POST name: {0}".format(random.random()))
            response1 = c.post('/api/v1/spot/', json_string1, content_type="application/json", follow=False)
            json_string2 = '{"name":"%s","capacity":"10", "location": {"latitude": 50, "longitude": -30},"extended_info":{"has_outlets":"true", "has_outlets":"true", "has_scanner":"true", "has_projector":"true", "has_computers":"true"}}' % ("testing POST name: {0}".format(random.random()))
            response2 = c.post('/api/v1/spot/', json_string2, content_type="application/json", follow=False)
            json_string3 = '{"name":"%s","capacity":"10", "location": {"latitude": 50, "longitude": -30},"extended_info":{"has_outlets":"true", "has_printing":"true", "has_projector":"true", "num_computers":"15", "has_computers":"true", "has_natural_light":"true"}}' % ("testing POST name: {0}".format(random.random()))
            response3 = c.post('/api/v1/spot/', json_string3, content_type="application/json", follow=False)

            url1 = response1["Location"]
            url2 = response2["Location"]
            url3 = response3["Location"]

            response = c.get(url1)
            spot_json1 = json.loads(response.content)
            response = c.get(url2)
            spot_json2 = json.loads(response.content)
            response = c.get(url3)
            spot_json3 = json.loads(response.content)

            self.assertEquals(spot_json1["extended_info"], json.loads(json_string1)['extended_info'], "extended_info was succesffuly POSTed")
            self.assertEquals(spot_json2["extended_info"], json.loads(json_string2)['extended_info'], "extended_info was succesffuly POSTed")
            self.assertEquals(spot_json3["extended_info"], json.loads(json_string3)['extended_info'], "extended_info was succesffuly POSTed")
