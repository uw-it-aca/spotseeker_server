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
class SpotPUTTest(TestCase):
    """ Tests updating Spot information via PUT.
    """

    def setUp(self):
        spot = Spot.objects.create(name="This is for testing PUT")
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
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30} }' % (new_name, new_capacity), content_type="application/json")
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

            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)
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

            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)
            self.assertEquals(response.status_code, 409, "An outdated etag leads to a conflict")

            updated_spot = Spot.objects.get(pk=self.spot.pk)
            self.assertEquals(updated_spot.name, intermediate_spot.name, "keeps the intermediate name w/ an outdated etag")
            self.assertEquals(updated_spot.capacity, intermediate_spot.capacity, "keeps the intermediate capacity w/ an outdate etag")

    def test_no_duplicate_extended_info(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing PUT name: {0}".format(random.random())
            new_capacity = 30

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30}, "extended_info": {"has_a_funky_beat": "true"} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30}, "extended_info": {"has_a_funky_beat": "true"} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="has_a_funky_beat")), 1, 'Only has 1 has_a_funky_beat SpotExtendedInfo object after 2 PUTs')

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30}, "extended_info": {"has_a_funky_beat": "of_course"} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="has_a_funky_beat")), 1, 'Only has 1 has_a_funky_beat SpotExtendedInfo object after 3 PUTs')
            self.assertEquals(self.spot.spotextendedinfo_set.get(key="has_a_funky_beat").value, 'of_course', 'SpotExtendedInfo was updated to the latest value on put.')

    def test_deleted_spot_info(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing PUT name: {0}".format(random.random())
            new_capacity = 30

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30}, "extended_info": {"eats_corn_pops": "true", "rages_hard": "true", "a": "true", "b": "true", "c": "true", "d": "true"} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="eats_corn_pops")), 1, 'Has 1 eats_corn_pops SpotExtendedInfo object after 1 PUT')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="rages_hard")), 1, 'Has 1 rages_hard SpotExtendedInfo object after 1 PUT')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="a")), 1, 'Has 1 a SpotExtendedInfo object after 1 PUT')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="b")), 1, 'Has 1 b SpotExtendedInfo object after 1 PUT')

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30}, "extended_info": {"eats_corn_pops": "true"} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="eats_corn_pops")), 1, 'Has 1 eats_corn_pops SpotExtendedInfo object after a PUT')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="rages_hard")), 0, 'Has 0 rages_hard SpotExtendedInfo object after a PUT and a DELETE')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="a")), 0, 'Has 0 a SpotExtendedInfo object after 1 PUT')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="b")), 0, 'Has 0 b SpotExtendedInfo object after 1 PUT')

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="eats_corn_pops")), 0, 'Has 0 eats_corn_pops SpotExtendedInfo object after a PUT and a DELETE')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="rages_hard")), 0, 'Has 0 rages_hard SpotExtendedInfo object after a PUT and a DELETE')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="a")), 0, 'Has 0 a SpotExtendedInfo object after 1 PUT')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="b")), 0, 'Has 0 b SpotExtendedInfo object after 1 PUT')

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="eats_corn_pops")), 0, 'Has 0 eats_corn_pops SpotExtendedInfo object after a PUT and a DELETE')

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "manager":"Yoda", "location": {"latitude": 55, "longitude": 30, "building_name": "Coruscant"} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            self.assertEquals(len(Spot.objects.get(name=new_name).manager), 4, 'Has 1 manager object after a PUT')
            self.assertEquals(len(Spot.objects.get(name=new_name).building_name), 9, 'Has 1 building_name object after a PUT')

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            self.assertEquals(len(Spot.objects.get(name=new_name).manager), 0, 'Has 0 manager objects after a PUT and a DELETE')
            self.assertEquals(len(Spot.objects.get(name=new_name).building_name), 0, 'Has 0 building_name objects after a PUT and a delete')

    def test_extended_info(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            new_name = "testing PUT name: {0}".format(random.random())
            new_capacity = 20
            json_string = '{"name":"%s","capacity":"%s", "location": {"latitude": 55, "longitude": 30}, "extended_info":{"has_outlets":"true"}}' % (new_name, new_capacity)
            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, json_string, content_type="application/json", If_Match=etag)
            spot_json = json.loads(response.content)
            extended_info = {"has_outlets": "true"}
            self.assertEquals(spot_json["extended_info"], extended_info, "extended_info was successfully PUT")

    def test_new_extended_info(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            name1 = "testing POST name: %s" % random.random()
            name2 = "testing POST name: %s" % random.random()
            name3 = "testing POST name: %s" % random.random()
            json_string1 = '{"name":"%s","capacity":"10", "location": {"latitude": 50, "longitude": -30},"extended_info":{"has_whiteboards":"true", "has_printing":"true", "has_displays":"true", "num_computers":"38", "has_natural_light":"true"}}' % name1
            response1 = c.post('/api/v1/spot/', json_string1, content_type="application/json", follow=False)
            json_string2 = '{"name":"%s","capacity":"10", "location": {"latitude": 50, "longitude": -30},"extended_info":{"has_outlets":"true", "has_outlets":"true", "has_scanner":"true", "has_projector":"true", "has_computers":"true"}}' % name2
            response2 = c.post('/api/v1/spot/', json_string2, content_type="application/json", follow=False)
            json_string3 = '{"name":"%s","capacity":"10", "location": {"latitude": 50, "longitude": -30},"extended_info":{"has_outlets":"true", "has_printing":"true", "has_projector":"true", "num_computers":"15", "has_computers":"true", "has_natural_light":"true"}}' % name3
            response3 = c.post('/api/v1/spot/', json_string3, content_type="application/json", follow=False)

            url1 = response1["Location"]
            url2 = response2["Location"]
            url3 = response3["Location"]

            response1 = c.get(url1)
            etag1 = response1["ETag"]
            response2 = c.get(url2)
            etag2 = response2["ETag"]
            response3 = c.get(url3)
            etag3 = response3["ETag"]

            new_json_string1 = '{"name":"%s","capacity":"10", "location": {"latitude": 50, "longitude": -30},"extended_info":{"has_whiteboards":"true", "something_new":"true", "has_printing":"true", "has_displays":"true", "num_computers":"38", "has_natural_light":"true"}}' % name1
            new_json_string2 = '{"name":"%s","capacity":"10", "location": {"latitude": 50, "longitude": -30},"extended_info":{"has_outlets":"true", "has_outlets":"true", "has_scanner":"true", "has_projector":"true", "has_computers":"true", "another_new":"yep it is"}}' % name2
            new_json_string3 = '{"name":"%s","capacity":"10", "location": {"latitude": 50, "longitude": -30},"extended_info":{"also_new":"ok", "another_new":"bleh", "has_outlets":"true", "has_printing":"true", "has_projector":"true", "num_computers":"15", "has_computers":"true", "has_natural_light":"true"}}' % name3

            response = c.put(url1, new_json_string1, content_type="application/json", If_Match=etag1)
            response = c.put(url2, new_json_string2, content_type="application/json", If_Match=etag2)
            response = c.put(url3, new_json_string3, content_type="application/json", If_Match=etag3)

            new_response1 = c.get(url1)
            spot_json1 = json.loads(new_response1.content)
            new_response2 = c.get(url2)
            spot_json2 = json.loads(new_response2.content)
            new_response3 = c.get(url3)
            spot_json3 = json.loads(new_response3.content)

            self.assertEqual(spot_json1["extended_info"], json.loads(new_json_string1)['extended_info'], "extended_info was succesffuly PUT")
            self.assertContains(new_response1, '"something_new": "true"')
            self.assertEqual(spot_json2["extended_info"], json.loads(new_json_string2)['extended_info'], "extended_info was succesffuly PUT")
            self.assertContains(new_response2, '"another_new": "yep it is"')
            self.assertEqual(spot_json3["extended_info"], json.loads(new_json_string3)['extended_info'], "extended_info was succesffuly PUT")
            self.assertContains(new_response3, '"also_new": "ok"')
            self.assertContains(new_response3, '"another_new": "bleh"')
