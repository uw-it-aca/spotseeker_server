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
@override_settings(SPOTSEEKER_AUTH_ADMINS=('demo_user',))
class JsonCachingTest(TestCase):
    """Tests the caching behavior
    """

    def setUp(self):
        self.cache = cache.get_cache('django.core.cache.backends.locmem.LocMemCache')
        self.cache.clear()
        spot1 = Spot.objects.create(name="This is for testing cache number 1", latitude="0", longitude="0")
        spot1.save()
        self.spot1 = spot1
        self.url1 = '/api/v1/spot/{0}'.format(self.spot1.pk)

    def test_get_spot(self):
        """tests if spot jsons are cached on the server when a client requests them
        """
        with patch.object(models, 'cache', self.cache):
            self.assertIsNone(self.cache.get(self.spot1.pk))
            client = Client()
            response = client.get(self.url1)
            self.assertIsNotNone(self.cache.get(self.spot1.pk))
            cache1 = models.cache.get(self.spot1.pk)
            self.assertEqual(cache1['name'], self.spot1.name)  # verify proper cached content

    def test_put_spot(self):
        """tests modifying spots through the api
        """
        with patch.object(models, 'cache', self.cache):
            client = Client()
            self.cache.clear()
            self.assertIsNone(self.cache.get(self.spot1.pk))  # cache should be emptied
            response = client.get(self.url1)
            etag = response['ETag']
            response1 = client.put(self.url1, '{"name":"whoop whoop changed number 1", "latitude": 0, "longitude": 0}', content_type="application/json", If_Match=etag, Foo='Bar')
            # cache should be empty or current
            cache1 = self.cache.get(self.spot1.pk)
            if cache1 is not None:
                self.assertEqual(cache1['name'], 'whoop whoop changed number 1', "Cache is up to date")
            else:
                self.assertIsNone(cache1, "Cache is empty")

    def test_delete_spot(self):
        """tests deleting spots through the api
        """
        with patch.object(models, 'cache', self.cache):
            client = Client()
            self.cache.clear()
            response = client.get(self.url1)
            etag = response["ETag"]
            the_pk = self.spot1.pk
            self.assertIsNotNone(self.cache.get(the_pk))  # cached object should be there
            response = client.delete(self.url1, If_Match=etag)
            self.assertEquals(response.status_code, 200, "Gives a GONE in response to a valid delete")

            try:
                test_spot = Spot.objects.get(pk=the_pk)
            except Exception as e:
                test_spot = None

            self.assertIsNone(test_spot, "Can't objects.get a deleted spot")
            self.assertIsNone(self.cache.get(the_pk))  # shouldn't be cached because its object is deleted

    def test_delete_spot_directly(self):
        """tests deleting spots through the admin
        """
        with patch.object(models, 'cache', self.cache):
            client = Client()
            self.cache.clear()
            response = client.get(self.url1)
            the_pk = self.spot1.pk
            self.assertIsNotNone(self.cache.get(the_pk))  # cached object should be there
            self.spot1.delete()
            self.assertIsNone(self.cache.get(the_pk))  # shouldn't be there

    def test_modify_spot(self):
        """tests modifying spots through the admin
        """
        with patch.object(models, 'cache', self.cache):
            client = Client()
            self.cache.clear()
            self.assertIsNone(self.cache.get(self.spot1.pk))  # cache should be emptied
            json = self.spot1.json_data_structure()
            self.assertIsNotNone(self.cache.get(self.spot1.pk))
            self.spot1.name = "All-Blacks Haka War Dance"
            self.spot1.save()
            self.assertIsNone(self.cache.get(self.spot1.pk))  # cache should be emptied of saved spot

    def test_spot_json_data_structure_cache(self):
        """tests that the caching happens in the json_data_structure model method
        """
        with patch.object(models, 'cache', self.cache):
            client = Client()
            self.cache.clear()
            self.assertIsNone(self.cache.get(self.spot1.pk))
            json = self.spot1.json_data_structure()
            self.assertIsNotNone(self.cache.get(self.spot1.pk))

    def tearDown(self):
        self.cache.clear()
