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

from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot
import simplejson as json
import random
from django.test.utils import override_settings
from mock import patch
from spotseeker_server import models


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
@override_settings(
    SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.'
                         'DefaultSpotForm')
@override_settings(
    SPOTSEEKER_SPOTEXTENDEDINFO_FORM='spotseeker_server.default_forms.spot.'
                                     'DefaultSpotExtendedInfoForm')
@override_settings(SPOTSEEKER_AUTH_ADMINS=('demo_user',))
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
        c = Client()
        response = c.put(self.url,
                         'this is just text',
                         content_type="application/json",
                         If_Match=self.spot.etag)
        self.assertEqual(response.status_code, 400)

    def test_invalid_url(self):
        c = Client()
        response = c.put("/api/v1/spot/aa", '{}',
                         content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_invalid_id_too_high(self):
        c = Client()
        test_id = self.spot.pk + 10000
        test_url = '/api/v1/spot/{0}'.format(test_id)
        response = c.put(test_url, '{}', content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_empty_json(self):
        c = Client()
        response = c.put(self.url,
                         '{}',
                         content_type="application/json",
                         If_Match=self.spot.etag)
        self.assertEqual(response.status_code, 400)

    def test_valid_json_no_etag(self):
        c = Client()
        new_name = "testing PUT name: {0}".format(random.random())
        new_capacity = 10
        response = c.put(self.url,
                         '{"name":"%s","capacity":"%d", "location": '
                         '{"latitude": 55, "longitude": 30} }'
                         % (new_name, new_capacity),
                         content_type="application/json")
        self.assertEqual(response.status_code,
                         400)

        updated_spot = Spot.objects.get(pk=self.spot.pk)
        self.assertEqual(updated_spot.name,
                         self.spot.name,
                         "No etag - same name")
        self.assertEqual(updated_spot.capacity,
                         self.spot.capacity,
                         "no etag - same capacity")

    def test_valid_json_valid_etag(self):
        user, created = User.objects.get_or_create(username='demo_user')
        c = Client()
        c.login(username=user.username)
        new_name = "testing PUT name: {0}".format(random.random())
        new_capacity = 20

        response = c.get(self.url)
        etag = response["ETag"]

        response = c.put(self.url,
                         '{"name":"%s","capacity":"%d", "location": '
                         '{"latitude": 55, "longitude": 30} }'
                         % (new_name, new_capacity),
                         content_type="application/json",
                         If_Match=etag)
        self.assertEqual(response.status_code, 200)

        updated_spot = Spot.objects.get(pk=self.spot.pk)
        self.assertEqual(updated_spot.name, new_name)
        self.assertEqual(updated_spot.capacity, new_capacity)

    def test_valid_json_outdated_etag(self):
        c = Client()
        new_name = "testing PUT name: {0}".format(random.random())
        new_capacity = 30

        response = c.get(self.url)
        etag = response["ETag"]

        intermediate_spot = Spot.objects.get(pk=self.spot.pk)
        intermediate_spot.name = "This interferes w/ the PUT"
        intermediate_spot.save()

        response = c.put(self.url,
                         '{"name":"%s","capacity":"%d", "location": '
                         '{"latitude": 55, "longitude": 30} }'
                         % (new_name, new_capacity),
                         content_type="application/json",
                         If_Match=etag)
        self.assertEqual(response.status_code,
                         409,
                         "An outdated etag leads to a conflict")

        updated_spot = Spot.objects.get(pk=self.spot.pk)
        self.assertEqual(updated_spot.name,
                         intermediate_spot.name)
        self.assertEqual(updated_spot.capacity,
                         intermediate_spot.capacity)

    def test_no_duplicate_extended_info(self):
        c = Client()
        new_name = "testing PUT name: {0}".format(random.random())
        new_capacity = 30

        response = c.get(self.url)
        etag = response["ETag"]
        response = c.put(self.url,
                         '{"name":"%s","capacity":"%d", "location": '
                         '{"latitude": 55, "longitude": 30}, '
                         '"extended_info": {"has_a_funky_beat": "true"} }'
                         % (new_name, new_capacity),
                         content_type="application/json",
                         If_Match=etag)

        response = c.get(self.url)
        etag = response["ETag"]
        response = c.put(self.url,
                         '{"name":"%s","capacity":"%d", "location": '
                         '{"latitude": 55, "longitude": 30}, '
                         '"extended_info": {"has_a_funky_beat": "true"} }'
                         % (new_name, new_capacity),
                         content_type="application/json",
                         If_Match=etag)

        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(
                key="has_a_funky_beat")),
            1)

        response = c.get(self.url)
        etag = response["ETag"]
        response = c.put(self.url,
                         '{"name":"%s","capacity":"%d", "location": '
                         '{"latitude": 55, "longitude": 30}, '
                         '"extended_info": {"has_a_funky_beat": '
                         '"of_course"} }'
                         % (new_name, new_capacity),
                         content_type="application/json",
                         If_Match=etag)

        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(
                key="has_a_funky_beat")),
            1)
        self.assertEqual(
            self.spot.spotextendedinfo_set.get(
                key="has_a_funky_beat").value,
            'of_course')

    def test_deleted_spot_info(self):
        c = Client()
        new_name = "testing PUT name: {0}".format(random.random())
        new_capacity = 30

        response = c.get(self.url)
        etag = response["ETag"]
        response = c.put(self.url,
                         '{"name":"%s","capacity":"%d", "location": '
                         '{"latitude": 55, "longitude": 30}, '
                         '"extended_info": {"eats_corn_pops": "true", '
                         '"rages_hard": "true", "a": "true", "b": "true", '
                         '"c": "true", "d": "true"} }'
                         % (new_name, new_capacity),
                         content_type="application/json",
                         If_Match=etag)

        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(
                key="eats_corn_pops")),
            1)
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(
                key="rages_hard")),
            1)
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(
                key="a")),
            1)
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(
                key="b")),
            1)

        response = c.get(self.url)
        etag = response["ETag"]
        response = c.put(self.url,
                         '{"name":"%s","capacity":"%d", "location": '
                         '{"latitude": 55, "longitude": 30}, '
                         '"extended_info": {"eats_corn_pops": "true"} }'
                         % (new_name, new_capacity),
                         content_type="application/json",
                         If_Match=etag)

        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(
                key="eats_corn_pops")),
            1)
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(
                key="rages_hard")),
            0)
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(
                key="a")),
            0)
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(
                key="b")),
            0)

        response = c.get(self.url)
        etag = response["ETag"]
        response = c.put(self.url,
                         '{"name":"%s","capacity":"%d", "location": '
                         '{"latitude": 55, "longitude": 30} }'
                         % (new_name, new_capacity),
                         content_type="application/json",
                         If_Match=etag)

        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(
                key="eats_corn_pops")),
            0)
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(
                key="rages_hard")),
            0)
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(
                key="a")),
            0)
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(
                key="b")),
            0)

        response = c.get(self.url)
        etag = response["ETag"]
        response = c.put(self.url,
                         '{"name":"%s","capacity":"%d", "location": '
                         '{"latitude": 55, "longitude": 30} }'
                         % (new_name, new_capacity),
                         content_type="application/json",
                         If_Match=etag)

        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(
                key="eats_corn_pops")),
            0)

        response = c.get(self.url)
        etag = response["ETag"]
        response = c.put(self.url,
                         '{"name":"%s","capacity":"%d", "manager":"Yoda", '
                         '"location": {"latitude": 55, "longitude": 30, '
                         '"building_name": "Coruscant"} }'
                         % (new_name, new_capacity),
                         content_type="application/json",
                         If_Match=etag)

        self.assertEqual(
            len(Spot.objects.get(name=new_name).manager),
            4)
        self.assertEqual(
            len(Spot.objects.get(name=new_name).building_name),
            9)

        response = c.get(self.url)
        etag = response["ETag"]
        response = c.put(self.url,
                         '{"name":"%s","capacity":"%d", "location": '
                         '{"latitude": 55, "longitude": 30} }'
                         % (new_name, new_capacity),
                         content_type="application/json",
                         If_Match=etag)

        self.assertEqual(
            len(Spot.objects.get(name=new_name).manager),
            0)
        self.assertEqual(
            len(Spot.objects.get(name=new_name).building_name),
            0)

    def test_extended_info(self):
        c = Client()
        new_name = "testing PUT name: {0}".format(random.random())
        new_capacity = 20
        json_string = ('{"name":"%s","capacity":"%s", "location": '
                       '{"latitude": 55, "longitude": 30}, '
                       '"extended_info":{"has_outlets":"true"}}'
                       % (new_name, new_capacity))
        response = c.get(self.url)
        etag = response["ETag"]
        response = c.put(self.url, json_string,
                         content_type="application/json",
                         If_Match=etag)
        spot_json = json.loads(response.content)
        extended_info = {"has_outlets": "true"}
        self.assertEqual(spot_json["extended_info"], extended_info)

    def test_new_extended_info(self):
        c = Client()
        name1 = "testing POST name: %s" % random.random()
        name2 = "testing POST name: %s" % random.random()
        name3 = "testing POST name: %s" % random.random()
        json_string1 = ('{"name":"%s","capacity":"10", "location": '
                        '{"latitude": 50, "longitude": -30},'
                        '"extended_info":{"has_whiteboards":"true", '
                        '"has_printing":"true", "has_displays":"true", '
                        '"num_computers":"38", "has_natural_light":'
                        '"true"}}' % name1)
        response1 = c.post('/api/v1/spot/', json_string1,
                           content_type="application/json", follow=False)
        json_string2 = ('{"name":"%s","capacity":"10", "location": '
                        '{"latitude": 50, "longitude": -30},'
                        '"extended_info":{"has_outlets":"true", '
                        '"has_outlets":"true", "has_scanner":"true", '
                        '"has_projector":"true", "has_computers":"true"}}'
                        % name2)
        response2 = c.post('/api/v1/spot/', json_string2,
                           content_type="application/json", follow=False)
        json_string3 = ('{"name":"%s","capacity":"10", "location": '
                        '{"latitude": 50, "longitude": -30},'
                        '"extended_info":{"has_outlets":"true", '
                        '"has_printing":"true", "has_projector":"true", '
                        '"num_computers":"15", "has_computers":"true", '
                        '"has_natural_light":"true"}}' % name3)
        response3 = c.post('/api/v1/spot/', json_string3,
                           content_type="application/json", follow=False)

        url1 = response1["Location"]
        url2 = response2["Location"]
        url3 = response3["Location"]

        response1 = c.get(url1)
        etag1 = response1["ETag"]
        response2 = c.get(url2)
        etag2 = response2["ETag"]
        response3 = c.get(url3)
        etag3 = response3["ETag"]

        new_json_string1 = ('{"name":"%s","capacity":"10", "location": '
                            '{"latitude": 50, "longitude": -30},'
                            '"extended_info":{"has_whiteboards":"true", '
                            '"something_new":"true", "has_printing":'
                            '"true", "has_displays":"true", '
                            '"num_computers":"38", "has_natural_light":'
                            '"true"}}' % name1)
        new_json_string2 = ('{"name":"%s","capacity":"10", "location": '
                            '{"latitude": 50, "longitude": -30},'
                            '"extended_info":{"has_outlets":"true", '
                            '"has_outlets":"true", "has_scanner":"true", '
                            '"has_projector":"true", "has_computers":'
                            '"true", "another_new":"yep it is"}}'
                            % name2)
        new_json_string3 = ('{"name":"%s","capacity":"10", "location": '
                            '{"latitude": 50, "longitude": -30},'
                            '"extended_info":{"also_new":"ok", '
                            '"another_new":"bleh", "has_outlets":"true", '
                            '"has_printing":"true", "has_projector":'
                            '"true", "num_computers":"15", '
                            '"has_computers":"true", "has_natural_light":'
                            '"true"}}' % name3)

        response = c.put(url1, new_json_string1,
                         content_type="application/json", If_Match=etag1)
        response = c.put(url2, new_json_string2,
                         content_type="application/json", If_Match=etag2)
        response = c.put(url3, new_json_string3,
                         content_type="application/json", If_Match=etag3)

        new_response1 = c.get(url1)
        spot_json1 = json.loads(new_response1.content)
        new_response2 = c.get(url2)
        spot_json2 = json.loads(new_response2.content)
        new_response3 = c.get(url3)
        spot_json3 = json.loads(new_response3.content)

        self.assertEqual(spot_json1["extended_info"],
                         json.loads(new_json_string1)['extended_info'])
        self.assertContains(new_response1, '"something_new": "true"')
        self.assertEqual(spot_json2["extended_info"],
                         json.loads(new_json_string2)['extended_info'])
        self.assertContains(new_response2,
                            '"another_new": "yep it is"')
        self.assertEqual(spot_json3["extended_info"],
                         json.loads(new_json_string3)['extended_info'])
        self.assertContains(new_response3, '"also_new": "ok"')
        self.assertContains(new_response3, '"another_new": "bleh"')
