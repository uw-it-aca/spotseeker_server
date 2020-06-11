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

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
import random
from string import ascii_lowercase

from spotseeker_server.models import Spot, Item, ItemExtendedInfo
try:
    xrange
except NameError:
    xrange = range


@override_settings(
    SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
    SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.'
                         'DefaultSpotForm')
class ItemModelTest(TestCase):
    """ Tests Item model data relations and retrieval. """

    def setUp(self):
        # create a Spot
        self.spot = Spot.objects.create(name='spot %s' % randstring())
        self.spot_id = self.spot.pk

        # Item category and subcategory
        self.category = 'Stuff'
        self.subcategory = 'Thing'

        # create an item
        self.checkout_item = Item.objects.create(
            name='an item',
            spot=self.spot,
            item_category=self.category,
            item_subcategory=self.subcategory)

        # create 4 items extended info
        for i in xrange(1, 5):
            ItemExtendedInfo.objects.create(
                item=self.checkout_item,
                key='key %s' % i,
                value='value %s' % i)

    def tearDown(self):
        # Deleting the spot cascade deletes the item and IEI
        self.spot.delete()

    def test_item_json(self):
        # get the Spot json
        test_spot = Spot.objects.get(pk=self.spot_id)
        json_data = test_spot.json_data_structure()
        self.assertIn('items', json_data)
        for item in json_data['items']:
            # assert that the Spot json contains the Item
            self.assertIn('name', item)
            self.assertEqual(item['name'], self.checkout_item.name)

            # assert Item category and subcategory
            self.assertEqual(item['category'], self.category)
            self.assertEqual(item['subcategory'], self.subcategory)
            self.assertIn('extended_info', item)

            prev_key = None
            prev_value = None

            for ei_key, ei_value in item['extended_info'].items():
                self.assertIn('key ', ei_key)
                self.assertIn('value ', ei_value)
                # Also make sure each one is unique
                self.assertNotEqual(ei_key, prev_key)
                self.assertNotEqual(ei_value, prev_value)

                prev_key = ei_key
                prev_value = ei_value


def randstring():
    return ''.join(random.choice(ascii_lowercase) for n in range(25))
