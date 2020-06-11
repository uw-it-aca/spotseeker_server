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
from spotseeker_server.models import Spot
import simplejson as json
import random
from django.test.utils import override_settings
import copy
from spotseeker_server.test import utils_test

try:
  basestring
except NameError:
  basestring = str

try:
    from unittest import skip
except ImportError:
    def skip(*args, **kwargs):
        def inner(self):
            pass
        return inner


@override_settings(
    SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
    SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.'
                         'DefaultSpotForm',
    SPOTSEEKER_SPOTEXTENDEDINFO_FORM='spotseeker_server.default_forms.spot.'
                                     'DefaultSpotExtendedInfoForm',
    SPOTSEEKER_AUTH_ADMINS=('demo_user',))
class SpotPOSTTest(TestCase):
    """ Tests creating a new Spot via POST.  """

    @staticmethod
    def random_name():
        return 'testing POST name: %s' % random.random()

    def post_spot(self, data):
        """
        Posts a spot with the test client. Can accept either a string or a json
        object.
        """
        if not isinstance(data, basestring):
            data = json.dumps(data)
        return self.client.post('/api/v1/spot/', data,
                                content_type='application/json',
                                follow=False)

    def test_valid_json(self):
        c = self.client
        new_name = self.random_name()
        new_capacity = 10
        spot_data = utils_test.get_spot(new_name, new_capacity)

        response = self.post_spot(spot_data)

        self.assertEquals(response.status_code, 201,
                          "Spot did not get created")
        self.assertIn("Location", response,
                      "Did not find Location header in response")

        self.spot = Spot.objects.get(name=new_name)

        self.assertEqual(response["Location"],
                         'http://testserver' + self.spot.rest_url())

        get_response = c.get(response["Location"])
        self.assertEqual(get_response.status_code, 200)

        spot_json = json.loads(get_response.content)

        self.assertEqual(
            spot_json["name"],
            new_name, "Did not find correct name in response")
        self.assertEqual(
            spot_json["capacity"],
            new_capacity, "Did not find correct capacity in response")

    def test_non_json(self):
        """ Attempt to post a json string instead of object """
        response = self.post_spot('just a string')
        self.assertEquals(response.status_code, 400)

    def test_invalid_json(self):
        """ Attempt to post an empty object """
        response = self.post_spot('{}')
        self.assertEquals(response.status_code, 400)

    def test_extended_info(self):
        """
        Tests a single extended_info field to ensure that it will save
        correctly.
        """
        new_name = self.random_name()
        new_capacity = 10
        spot_data = {
            'name': new_name,
            'capacity': new_capacity,
            'location': {'latitude': 50, 'longitude': -30},
            'extended_info': {'has_outlets': 'true'}
        }
        json_string = json.dumps(spot_data)
        response = self.post_spot(json_string)
        get_response = self.client.get(response["Location"])
        spot_json = json.loads(get_response.content)
        self.assertEquals(
            spot_json['extended_info'],
            spot_data['extended_info'], "Did get the same EI we posted")

    def test_multiple_correct_extended_info(self):
        """
        Test that multiple extended info fields can be saved correctly.
        """
        urls = {}
        spot_0 = {
            'name': self.random_name(),
            'capacity': 10,
            'location': {'latitude': 50, 'longitude': -30},
            'extended_info': {
                'has_whiteboards': 'true',
                'has_printing': 'true',
                'has_displays': 'true',
                'num_computers': '38',
                'has_natural_light': 'true',
            }
        }

        spot_1 = copy.deepcopy(spot_0)
        spot_1['name'] = self.random_name()
        spot_1['extended_info'] = dict.fromkeys(
            ('has_outlets', 'has_scanner', 'has_projector', 'has_computers'),
            'true')

        spot_2 = copy.deepcopy(spot_1)
        spot_2['name'] = self.random_name()
        spot_2['extended_info'] = dict.fromkeys(
            ('has_outlets', 'has_printing', 'has_projector', 'has_computers',
             'has_natural_light'), 'true')
        spot_2['extended_info']['num_computers'] = '15'

        in_data = {0: spot_0, 1: spot_1, 2: spot_2}

        for idx, spot_data in in_data.items():
            response = self.post_spot(spot_data)
            urls[idx] = response['Location']

        for idx, url in urls.items():
            out_json = json.loads(self.client.get(url).content)
            expected_ei = in_data[idx]['extended_info']
            actual_ei = out_json['extended_info']
            self.assertEqual(expected_ei, actual_ei)

    def test_create_spot_with_items(self):
        """
        Tests the creation of a spot with correct items data.
        """
        c = self.client

        new_name = self.random_name()
        new_capacity = 10

        spot_json = utils_test.get_spot(new_name, new_capacity)

        spot_json['items'].append(utils_test.get_item())

        response = self.post_spot(spot_json)

        # assert that the spot was created
        self.assertEqual(response.status_code, 201)

        # try to retrieve the spot and ensure that items are there
        get_response = c.get(response["Location"])

        json_response = json.loads(get_response.content)

        self.assertEqual(len(json_response["items"]), 1)

        original_item = spot_json['items'][0]
        item = json_response["items"][0]
        self.assertEqual(item["name"], original_item['name'])
        self.assertEqual(item["category"], original_item['category'])
        self.assertEqual(item["subcategory"], original_item['subcategory'])

    def test_create_spot_with_bad_items(self):
        """
        Tests the creation of a spot with malformed items data, both bad json
        and missing fields.
        """
        new_name = self.random_name()
        new_capacity = 10
        bad_spot_json = '{"name":"%s","capacity":"%d", "location": ' \
                        '{"latitude": 50, "longitude": -30}, "items" : [s ' \
                        '{"name" : "itemname", "category" : "itemcategory", '\
                        '"subcategory" : "itemsubcategory"}] }' \
                        % (new_name, new_capacity)

        response = self.post_spot(bad_spot_json)

        # bad json should return a 400
        self.assertEqual(response.status_code, 400)

        spot_json = {
            'name': self.random_name(),
            'capacity': new_capacity,
            'location': {'latitude': 50, 'longitude': -30},
            'items': [
                {
                 'name': 'itemname',
                 'category': 'itemcategory',
                 'subcategory': 'itemsubcategory',
                 'extended_info': {}
                 }
            ]
        }

        # delete some required fields from the JSON
        no_name_json = copy.deepcopy(spot_json)
        del no_name_json["items"][0]['name']

        no_category_json = copy.deepcopy(spot_json)
        del no_category_json["items"][0]['category']

        no_subcategory_json = copy.deepcopy(spot_json)
        del no_subcategory_json["items"][0]['subcategory']

        bad_json = (no_name_json, no_category_json, no_subcategory_json)
        messages = ('Item name validation failed to raise an error',
                    'Item category validation failed to raise an error',
                    'Item subcategory validation failed to raise an error')

        # all of these POSTs should fail with a 400
        for js, message in zip(bad_json, messages):
            response = self.post_spot(js)
            self.assertEqual(response.status_code, 400, message)

    def test_item_extended_info(self):
        """
        Tests to ensure that the item extended info is being saved on creation.
        """

        # todo : change to dict
        ei_keys = ("make_model", "customer_type", "auto_item_status")
        ei_values = ("itemmodel", "UW Student", "active")

        spot_json = utils_test.get_spot(self.random_name(), 20)

        spot_json['items'].append(utils_test.get_item())

        for key, value in zip(ei_keys, ei_values):
            spot_json['items'][0]['extended_info'][key] = value

        response = self.client.post('/api/v1/spot', json.dumps(spot_json),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 201)

        get_response = self.client.get(response['Location'])

        self.assertEqual(get_response.status_code, 200)

        json_response = json.loads(get_response.content)

        self.assertEqual(len(json_response["items"]), 1)

        self.assertIn('extended_info', spot_json['items'][0],
                      "No extended_info in the item!")

        # assert that values were correct
        for key, value in zip(ei_keys, ei_values):
            self.assertIn(key, json_response["items"][0]["extended_info"],
                          key + " not in item extended info!")

            self.assertEqual(json_response["items"][0]["extended_info"][key],
                             value, key + " was not " + value + ", was :" +
                             json_response["items"][0]["extended_info"][key])
