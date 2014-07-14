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

from django.test import TransactionTestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot
import simplejson as json
import random
from django.test.utils import override_settings
from mock import patch
from django.core import cache
from spotseeker_server import models


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
@override_settings(SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm')
@override_settings(SPOTSEEKER_SPOTEXTENDEDINFO_FORM='spotseeker_server.org_forms.uw_spot.UWSpotExtendedInfoForm')
@override_settings(SPOTSEEKER_AUTH_ADMINS=('demo_user',))
class UWSpotPOSTTest(TransactionTestCase):
    """ Tests creating a new Spot via POST.
    """

    def test_valid_json(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            json_string = '{"name":"%s","capacity":"%s","location":{"latitude": 55, "longitude": -30},"extended_info":{"has_whiteboards":"true","has_outlets":"true","manager":"Bob","organization":"UW"}}' % (new_name, new_capacity)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")
            self.assertIn("Location", response, "The response has a location header")

            self.spot = Spot.objects.get(name=new_name)

            self.assertEquals(response["Location"], "http://testserver" + self.spot.rest_url(), "The uri for the new spot is correct")

            get_response = c.get(response["Location"])
            self.assertEquals(get_response.status_code, 200, "OK in response to GETing the new spot")

            spot_json = json.loads(get_response.content)

            self.assertEquals(spot_json["name"], new_name, "The right name was stored")
            self.assertEquals(spot_json["capacity"], new_capacity, "The right capacity was stored")

    def test_non_json(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.post('/api/v1/spot/', 'just a string', content_type="application/json", follow=False)
            self.assertEquals(response.status_code, 400)

    def test_invalid_json(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.post('/api/v1/spot/', '{}', content_type="application/json", follow=False)
            self.assertEquals(response.status_code, 400)

    def test_uw_field_has_whiteboards(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            whiteboards = 12
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_whiteboards":"%s","has_outlets":"true","manager":"John","organization":"UW"}}' % (new_name, new_capacity, whiteboards)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because has_whiteboards field did not pass validation")

            whiteboards = 'true'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_whiteboards":"%s","has_outlets":"true","manager":"John","organization":"UW"}}' % (new_name, new_capacity, whiteboards)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_has_outlets(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            outlets = 12

            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_whiteboards":"false","manager":"Harry","organization":"UW"}}' % (new_name, new_capacity)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)
            self.assertEquals(response.status_code, 400, "Not created because has_outlets was not included")

            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_whiteboards":"false","has_outlets":"%s","manager":"Harry","organization":"UW"}}' % (new_name, new_capacity, outlets)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)
            self.assertEquals(response.status_code, 400, "Not created because has_outlets field did not pass validation")

            outlets = 'true'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_whiteboards":"true","has_outlets":"%s","manager":"Harry","organization":"UW"}}' % (new_name, new_capacity, outlets)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)
            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_has_printing(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            printer = 12
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","has_printing":"%s","manager":"Gary","organization":"UW"}}' % (new_name, new_capacity, printer)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because has_printing field did not pass validation")

            printer = 'true'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","has_printing":"%s","manager":"Gary","organization":"UW"}}' % (new_name, new_capacity, printer)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_has_scanner(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            scanner = 'There are none'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","has_scanner":"%s","manager":"Sally","organization":"UW"}}' % (new_name, new_capacity, scanner)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because has_scanner field did not pass validation")

            scanner = 'true'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","has_scanner":"%s","manager":"Sally","organization":"UW"}}' % (new_name, new_capacity, scanner)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_has_displays(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            has_displays = 'There are none'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","has_displays":"%s","manager":"Fred","organization":"UW"}}' % (new_name, new_capacity, has_displays)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because has_displays field did not pass validation")

            has_displays = 'true'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","has_displays":"%s","manager":"Fred","organization":"UW"}}' % (new_name, new_capacity, has_displays)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_has_projector(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            has_projector = 'There are none'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","has_projector":"%s","manager":"George","organization":"UW"}}' % (new_name, new_capacity, has_projector)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because has_projector field did not pass validation")

            has_projector = 'true'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","has_projector":"%s","manager":"George","organization":"UW"}}' % (new_name, new_capacity, has_projector)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_has_computers(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            computers = 'There are none'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","has_computers":"%s","manager":"Tina","organization":"UW"}}' % (new_name, new_capacity, computers)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because has_computers field did not pass validation")

            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","has_computers":"true","manager":"Tina","organization":"UW"}}' % (new_name, new_capacity)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_num_computers(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            computers = "invalid_int"
            json_string = '{"name":"%s","capacity":"%s","location":{"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","has_computers":"true","num_computers":"%s","manager":"Tina","organization":"UW"}}' % (new_name, new_capacity, computers)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)
            self.assertEquals(response.status_code, 400, "Make sure not to create the spot because num_computers field did not pass validation")

            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","has_computers":"true","num_computers":"15","manager":"Tina","organization":"UW"}}' % (new_name, new_capacity)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_has_natural_light(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            has_natural_light = 'Nope!'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","has_natural_light":"%s","manager":"Mary","organization":"UW"}}' % (new_name, new_capacity, has_natural_light)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because has_natural_light field did not pass validation")

            has_natural_light = 'true'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","has_natural_light":"%s","manager":"Mary","organization":"UW"}}' % (new_name, new_capacity, has_natural_light)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_noise_level(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            noise_level = 'Rock Concert'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","noise_level":"%s","manager":"Patty","organization":"UW"}}' % (new_name, new_capacity, noise_level)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because noise_level field did not pass validation")

            noise_level = 'moderate'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","noise_level":"%s","manager":"Patty","organization":"UW"}}' % (new_name, new_capacity, noise_level)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_food_nearby(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            food_nearby = 'In the area'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","food_nearby":"%s","manager":"Kristy","organization":"UW"}}' % (new_name, new_capacity, food_nearby)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because food_nearby field did not pass validation")

            food_nearby = 'building'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","food_nearby":"%s","manager":"Kristy","organization":"UW"}}' % (new_name, new_capacity, food_nearby)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_reservable(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            reservable = 'You bet'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","reservable":"%s","manager":"Patty","organization":"UW"}}' % (new_name, new_capacity, reservable)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because reservable field did not pass validation")

            reservable = 'reservations'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_outlets":"true","reservable":"%s","manager":"Patty","organization":"UW"}}' % (new_name, new_capacity, reservable)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_location_description(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10

            desc = 'This is a description'
            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude":-30},"extended_info":{"has_outlets":"true","location_description":"%s","manager":"Patty","organization":"UW"}}' % (new_name, new_capacity, desc)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

            spot = Spot.objects.get(name=new_name)
            spot_desc = spot.spotextendedinfo_set.get(key='location_description').value

            self.assertEquals(desc, spot_desc, "The Spot's description matches what was POSTed.")

    def test_valid_json_but_invalid_extended_info(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10

            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude":-30},"extended_info":{"has_outlets":"true","manager":"Patty","organization":"UW"}}' % (new_name, new_capacity)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)
            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            bad_json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_whiteboards":"true","has_outlets":"wub wub wub wu wu wuhhhh WUB WUB WUBBBBUB","manager":"Sam","organization":"UW"}}' % (new_name, new_capacity)
            response = c.post('/api/v1/spot/', bad_json_string, content_type="application/json", follow=False)
            self.assertEquals(response.status_code, 400, "Doesn't add spot info with invalid extended info")
            self.assertEquals(Spot.objects.count(), 2, "Doesn't POST spots with invalid extended info")

    def test_valid_json_but_no_extended_info(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10

            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude":-30}}' % (new_name, new_capacity)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            error_message = json.loads(response.content)['error']
            self.assertEquals(error_message, "[u'UWSpot must have extended info']", "Doesn't add spot info with invalid extended info")
