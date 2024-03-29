# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from django.test.utils import override_settings
from spotseeker_server.models import (
    Spot,
    SpotExtendedInfo,
    Item,
    ItemExtendedInfo,
)
import simplejson as json
from mock import patch
from spotseeker_server import models

try:
    from unittest import skip
except ImportError:

    def skip(*args, **kwargs):
        def inner(self):
            pass

        return inner


@override_settings(SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok")
class SpotSearchItemTest(TestCase):
    """
    Tests on the implemented item filters. Checks whether the new filters work
    for item name, category, sub-category and extended_info.
    """

    def setUp(self):
        """
        Creates spots with items which have some extended_info.

        spot1 has customer UW, capacity 10, a dell laptop and a mac laptop.
        spot2 has customer UW, capacity 10, a toyota and a dell laptop.
        spot3 has customer UW, customer UW, a mac laptop and a toyota.
        spot4 has customer UW, capacity 10, and a chevy.
        """
        self.spot1 = Spot.objects.create(name="spotone")
        self.item1 = Item.objects.create(
            spot=self.spot1,
            name="itemone",
            item_category="laptop",
            item_subcategory="dell",
        )
        self.extended1 = ItemExtendedInfo(
            item=self.item1, key="capacity", value="10"
        )
        self.extended1.save()
        self.item2 = Item.objects.create(
            spot=self.spot1,
            name="itemtwo",
            item_category="laptop",
            item_subcategory="mac",
        )
        self.extended1 = ItemExtendedInfo(
            item=self.item2, key="customer", value="UW"
        )
        self.extended1.save()
        self.spot1.save()

        self.spot2 = Spot.objects.create(name="spottwo")
        self.item1 = Item.objects.create(
            spot=self.spot2,
            name="itemone",
            item_category="car",
            item_subcategory="toyota",
        )
        self.extended1 = ItemExtendedInfo(
            item=self.item1, key="customer", value="UW"
        )
        self.extended1.save()
        self.item2 = Item.objects.create(
            spot=self.spot2,
            name="itemtwo",
            item_category="laptop",
            item_subcategory="dell",
        )
        self.extended1 = ItemExtendedInfo(
            item=self.item2, key="capacity", value="10"
        )
        self.extended1.save()
        self.spot2.save()

        self.spot3 = Spot.objects.create(name="spotthree")
        self.item1 = Item.objects.create(
            spot=self.spot3,
            name="itemthree",
            item_category="laptop",
            item_subcategory="mac",
        )
        self.extended1 = ItemExtendedInfo(
            item=self.item1, key="customer", value="UW"
        )
        self.extended1.save()
        self.item2 = Item.objects.create(
            spot=self.spot3,
            name="itemtwo",
            item_category="car",
            item_subcategory="toyota",
        )
        self.extended1 = ItemExtendedInfo(
            item=self.item2, key="customer", value="UW"
        )
        self.extended1.save()
        self.spot3.save()

        self.spot4 = Spot.objects.create(name="spotfour")
        self.item1 = Item.objects.create(
            spot=self.spot4,
            name="itemthree",
            item_category="car",
            item_subcategory="chevy",
        )
        self.extended1 = ItemExtendedInfo(
            item=self.item1, key="customer", value="UW"
        )
        self.extended1.save()
        self.extended2 = ItemExtendedInfo(
            item=self.item1, key="capacity", value="10"
        )
        self.extended2.save()
        self.spot4.save()

    def tearDown(self):
        """
        Deletes every spot and item after the tests have been executed.
        """
        self.item1.delete()
        self.item2.delete()
        self.extended1.delete()
        self.extended2.delete()
        self.spot1.delete()
        self.spot2.delete()
        self.spot3.delete()
        self.spot4.delete()

    def item_common(self, field, cases):
        for case in cases:
            response = self.client.get(
                "/api/v1/spot", {"item:%s" % field: "%s" % case}
            )
            self.assertEquals(
                response["Content-Type"],
                "application/json",
                "Expected a valid JSON.",
            )
            spots = json.loads(response.content)
            self.assertEquals(
                len(spots),
                int(cases[case]),
                "Expected %s spots in the JSON for %s" % (cases[case], case),
            )
            for spot in spots:
                validity = False
                for item in spot["items"]:
                    if item["%s" % field] == case:
                        validity = True
                self.assertEquals(
                    validity, True, "Invalid spot returned for %s" % field
                )

    def test_item_name(self):
        """
        Runs tests against different names and verifies the filters work
        as intended.
        """
        field = "name"
        cases = {"itemone": "2", "itemtwo": "3", "itemthree": "2", "": "0"}
        self.item_common(field, cases)

    def test_item_category(self):
        """
        Runs tests against different categories and verifies the filters work
        as intended.
        """
        field = "category"
        cases = {"laptop": "3", "car": "3", "": "0", "invalid": "0"}
        self.item_common(field, cases)

    def test_item_subcategory(self):
        """
        Runs tests against different subcategories and verifies the filters
        work as intended.
        """
        field = "subcategory"
        cases = {"dell": "2", "mac": "2", "toyota": "2", "chevy": "1", "": "0"}
        self.item_common(field, cases)

    def item_ei_common(self, field, cases):
        for case in cases:
            response = self.client.get(
                "/api/v1/spot", {"item:extended_info:%s" % field: "%s" % case}
            )
            self.assertEquals(
                response["Content-Type"],
                "application/json",
                "Expected a valid JSON.",
            )
            spots = json.loads(response.content)
            self.assertEquals(
                len(spots),
                int(cases[case]),
                "Expected %s spots in the JSON for %s" % (cases[case], case),
            )
            for spot in spots:
                validity = False
                for item in spot["items"]:
                    for ei in item["extended_info"]:
                        if ei == field:
                            if item["extended_info"]["%s" % ei] == case:
                                validity = True
                self.assertEquals(
                    validity, True, "Invalid spot returned for %s" % field
                )

    def test_item_ei(self):
        """
        Runs tests against different extended_infos and verifies the filters
        work as intended.
        """
        field = "customer"
        cases = {"UW": "4", "10": "0", "Berkeley": "0"}
        self.item_ei_common(field, cases)
        field = "capacity"
        cases = {"10": "3", "UW": "0", "": "0"}
        self.item_ei_common(field, cases)
        field = ""
        cases = {"10": "0", "UW": "0"}
        self.item_ei_common(field, cases)

    def test_multi_subcategory_item(self):
        """
        Tests filtering on multiple subcategories.
        """
        response = self.client.get(
            "/api/v1/spot", {"item:subcategory": ["dell", "toyota"]}
        )
        self.assertEquals(
            response["Content-Type"],
            "application/json",
            "Expected a valid JSON.",
        )
        spots = json.loads(response.content)
        self.assertEquals(
            len(spots), 3, "Expected 3 spot in the JSON for dell and toyota"
        )

    def test_multi_item_extended_info(self):
        """
        Tests filtering on multiple item extended info.
        """
        response = self.client.get(
            "/api/v1/spot",
            {
                "item:extended_info:capacity": "10",
                "item:extended_info:customer": "UW",
            },
        )
        self.assertEquals(
            response["Content-Type"],
            "application/json",
            "Expected a valid JSON.",
        )
        spots = json.loads(response.content)
        self.assertEquals(
            len(spots),
            4,
            "Expected 4 spots in the JSON for ei:capacity and ei:customer",
        )

    def test_item_category_and_extended_info(self):
        """
        Tests filtering on a category and an item extended info.
        """
        response = self.client.get(
            "/api/v1/spot",
            {"item:category": "laptop", "item:extended_info:capacity": "10"},
        )
        self.assertEquals(
            response["Content-Type"],
            "application/json",
            "Expected a valid JSON.",
        )
        spots = json.loads(response.content)
        self.assertEquals(
            len(spots),
            4,
            "Expected 4 spots in the JSON for laptop and ei:capacity",
        )

    def test_invalid_item_key(self):
        """
        Tests filtering against keys that don't exist.
        """
        response = self.client.get(
            "/api/v1/spot",
            {
                "item:category": "laptop",
                "item:extended_info:capacity": "10",
                "invalid": "23",
            },
        )
        self.assertEquals(
            response["Content-Type"],
            "application/json",
            "Expected a valid JSON.",
        )
        spots = json.loads(response.content)
        self.assertEquals(
            len(spots), 4, "Expected 4 spots in the JSON. Ignores invalid key."
        )

    def test_nonexisting_item_value(self):
        """
        Tests filtering against values that don't exist.
        """
        response = self.client.get(
            "/api/v1/spot",
            {"item:category": "laptop", "item:extended_info:capacity": "100"},
        )
        self.assertEquals(
            response["Content-Type"],
            "application/json",
            "Expected a valid JSON.",
        )
        spots = json.loads(response.content)
        self.assertEquals(
            len(spots),
            3,
            "Expected 3 spots in the JSON. Doesn't ignore invalid value.",
        )
