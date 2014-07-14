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
from spotseeker_server.models import Spot, SpotExtendedInfo
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
class UWSpotPUTTest(TransactionTestCase):
    """ Tests updating Spot information via PUT.
    """

    def setUp(self):
        spot = Spot.objects.create(name="This is for testing PUT")
        SpotExtendedInfo.objects.create(spot=spot, key="aw_yisss", value="breadcrumbs")
        spot.save()
        self.spot = spot

        url = '/api/v1/spot/{0}'.format(self.spot.pk)
        self.url = url

    def test_bad_json(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.put(self.url, 'this is just text', content_type="application/json", If_Match=self.spot.etag)
            self.assertEquals(response.status_code, 400, "Rejects non-json")

    def test_invalid_url(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.put("/api/v1/spot/aa", '{}', content_type="application/json")
            self.assertEquals(response.status_code, 404, "Rejects a non-numeric url")

    def test_invalid_id_too_high(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            test_id = self.spot.pk + 10000
            test_url = '/api/v1/spot/{0}'.format(test_id)
            response = c.put(test_url, '{}', content_type="application/json")
            self.assertEquals(response.status_code, 404, "Rejects an id that doesn't exist yet (no PUT to create)")

    def test_empty_json(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            response = c.put(self.url, '{}', content_type="application/json", If_Match=self.spot.etag)
            self.assertEquals(response.status_code, 400, "Rejects an empty body")

    def test_valid_json_no_etag(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing PUT name: {0}".format(random.random())
            new_capacity = 10
            response = c.put(self.url, '{{"name":"{0}","capacity":"{1}"}}'.format(new_name, new_capacity), content_type="application/json")
            self.assertEquals(response.status_code, 400, "Bad request w/o an etag")

            updated_spot = Spot.objects.get(pk=self.spot.pk)
            self.assertEquals(updated_spot.name, self.spot.name, "No etag - same name")
            self.assertEquals(updated_spot.capacity, self.spot.capacity, "no etag - same capacity")

    def test_valid_json_valid_etag(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing PUT name: {0}".format(random.random())
            new_capacity = 20

            response = c.get(self.url)
            etag = response["ETag"]

            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_whiteboards":"true","has_outlets":"true","manager":"Sam","organization":"UW"}}' % (new_name, new_capacity)
            response = c.put(self.url, json_string, content_type="application/json", If_Match=etag)
            self.assertEquals(response.status_code, 200, "Accepts a valid json string")

            updated_spot = Spot.objects.get(pk=self.spot.pk)
            self.assertEquals(updated_spot.name, new_name, "a valid PUT changes the name")
            self.assertEquals(updated_spot.capacity, new_capacity, "a valid PUT changes the capacity")

    def test_valid_json_outdated_etag(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing PUT name: {0}".format(random.random())
            new_capacity = 30

            response = c.get(self.url)
            etag = response["ETag"]

            intermediate_spot = Spot.objects.get(pk=self.spot.pk)
            intermediate_spot.name = "This interferes w/ the PUT"
            intermediate_spot.save()

            response = c.put(self.url, '{{"name":"{0}","capacity":"{1}"}}'.format(new_name, new_capacity), content_type="application/json", If_Match=etag)
            self.assertEquals(response.status_code, 409, "An outdated etag leads to a conflict")

            updated_spot = Spot.objects.get(pk=self.spot.pk)
            self.assertEquals(updated_spot.name, intermediate_spot.name, "keeps the intermediate name w/ an outdated etag")

    def test_valid_json_but_invalid_extended_info(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing PUT name: {0}".format(random.random())
            new_capacity = 20

            response = c.get(self.url)
            etag = response["ETag"]

            json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_whiteboards":"true","has_outlets":"true","has_computers":"true","num_computers":"10","manager":"Sam","organization":"UW"}}' % (new_name, new_capacity)
            response = c.put(self.url, json_string, content_type="application/json", If_Match=etag)
            self.assertEquals(response.status_code, 200, "Accepts a valid json string")

            # test: invalid extended info value
            response = c.get(self.url)
            etag = response["ETag"]
            updated_json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_whiteboards":"true","has_outlets":"wub wub wub wu wu wuhhhh WUB WUB WUBBBBUB", "has_computers":"true", "num_computers":"10","manager":"Sam","organization":"UW"}}' % (new_name, new_capacity)

            response = c.put(self.url, updated_json_string, content_type="application/json", If_Match=etag)
            self.assertEquals(response.status_code, 400, "Doesn't update spot info with invalid extended info")

            response = c.get(self.url)
            self.assertEquals(json.loads(json_string)['extended_info'], json.loads(response.content)['extended_info'], "Doesn't update spot info with invalid extended info")
            
            # test: invalid int value
            invalid_int = "invalid_int"
            invalid_int_json_string = '{"name":"%s","capacity":"%s","location": {"latitude": 55, "longitude": -30},"extended_info":{"has_whiteboards":"true","has_outlets":"true", "has_computers":"true", "num_computers":"%s","manager":"Sam","organization":"UW"}}' % (new_name, new_capacity, invalid_int)

            response = c.put(self.url, invalid_int_json_string, content_type="application/json", If_Match=etag)
            self.assertEquals(response.status_code, 400, "Doesn't update spot info with invalid int value")

            response = c.get(self.url)
            self.assertEquals(json.loads(json_string)['extended_info'], json.loads(response.content)['extended_info'], "Doesn't update spot info with invalid int value")
