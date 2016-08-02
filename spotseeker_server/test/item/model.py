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

from spotseeker_server.models import Spot, Item, ItemExtendedInfo


@override_settings(
    SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
    SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.'
                         'DefaultSpotForm')
class ItemModelTest(TestCase):
    """ Tests Item model methods.
    """

    def setUp(self):
        # create a Spot
        self.spot = Spot()
        self.spot.name = "spot {0}".format(randstring())
        self.spot.save()

        self.spot_id = self.spot.pk

        # Item category and subcategory
        self.category = 'Stuff'
        self.subcategory = 'Thing'

        # create an item
        self.checkout_item = Item()
        self.checkout_item.name = 'an item'
        self.checkout_item.spot = self.spot
        self.checkout_item.category = self.category
        self.checkout_item.subcategory = self.subcategory
        self.checkout_item.save()

        # create 4 items extended info
        for i in range(1, 5):
            self.iei = ItemExtendedInfo()
            self.iei.item = self.checkout_item
            self.iei.key = "key " + str(i)
            self.iei.value = "value " + str(i)
            self.iei.save()

    def tearDown(self):
        self.spot.delete()
        self.checkout_item.delete()
        self.iei.delete()

    def test_item_json(self):
        # get the Spot json
        test_spot = Spot.objects.get(pk=self.spot_id)
        json_data = test_spot.json_data_structure()
        for item in json_data["items"]:
            # assert that the Spot json contains the Item
            self.assertTrue('items' in json_data)
            self.assertTrue('name' in item)
            self.assertTrue(item['name'] == self.checkout_item.name)

            # assert Item category and subcategory
            self.assertTrue(item['category'] == self.category)
            self.assertTrue(item['subcategory'] == self.subcategory)
            self.assertTrue('extended_info' in item)


def randstring():
    name = ''
    i = 0
    while i < 25:
        name += random.choice('qwertyuiopasdfghjklzxcvbnm')
        i += 1
    return name
