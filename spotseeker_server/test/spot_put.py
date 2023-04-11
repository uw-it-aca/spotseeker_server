# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot, Item
from django.test.utils import override_settings
from mock import patch
from spotseeker_server import models
import simplejson as json
import random
from spotseeker_server.test import utils_test
import copy

from past.builtins import basestring

try:
    from unittest import skip
except ImportError:

    def skip(*args, **kwargs):
        def inner(self):
            pass

        return inner


@override_settings(SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok")
@override_settings(
    SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms.spot."
    "DefaultSpotForm"
)
@override_settings(
    SPOTSEEKER_SPOTEXTENDEDINFO_FORM="spotseeker_server.default_forms.spot."
    "DefaultSpotExtendedInfoForm"
)
@override_settings(SPOTSEEKER_AUTH_ADMINS=("demo_user",))
class SpotPUTTest(TestCase):
    """Tests updating Spot information via PUT."""

    @staticmethod
    def random_name():
        return "testing PUT name: %s" % random.random()

    def setUp(self):
        spot = Spot.objects.create(name="This is for testing PUT")
        spot.save()
        self.spot = spot

        url = "/api/v1/spot/{0}".format(self.spot.pk)
        self.url = url

    def get_etag(self, url):
        """Returns the ETag from the given URL."""
        response = self.client.get(url)

        if "ETag" not in response:
            print("ETag not found for URL " + url)

        return response["ETag"]

    def put_spot(self, url, body):
        """PUTs a spot with the given URL and body.

        Will first fire a GET at that URL, and then retrieve the current ETag
        for said spot so that we can ensure that we do not cause conflicts.

        Body can either be a string or a dict.
        """
        if not isinstance(body, basestring):
            body = json.dumps(body)

        eTag = self.get_etag(url)
        return self.client.put(
            url, body, content_type="application/json", If_Match=eTag
        )

    def test_bad_json(self):
        """Tests that the spot PUT will reject invalid JSON"""
        response = self.put_spot(self.url, "this is just text")
        self.assertEqual(response.status_code, 400)

    def test_invalid_url(self):
        """Tests that our spot PUT url pattern will not match invalid URLs."""
        response = self.client.put(
            "/api/v1/spot/aa", "{}", content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

    def test_invalid_id_too_high(self):
        """Test that we cannot PUT to a spot that does not exist."""
        test_url = "/api/v1/spot/{0}".format(self.spot.pk + 10000)
        response = self.client.put(
            test_url, "{}", content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

    def test_empty_json(self):
        """Test that without required fields our spot will be rejected."""
        response = self.client.put(
            self.url, "{}", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_valid_json_no_etag(self):
        """Test that an ETag is required to update a spot."""
        c = Client()
        new_name = "testing PUT name: {0}".format(random.random())
        new_capacity = 10
        response = c.put(
            self.url,
            '{"name":"%s","capacity":"%d", "location": '
            '{"latitude": 55, "longitude": 30} }' % (new_name, new_capacity),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

        updated_spot = Spot.objects.get(pk=self.spot.pk)
        self.assertEqual(
            updated_spot.name, self.spot.name, "No etag - same name"
        )
        self.assertEqual(
            updated_spot.capacity,
            self.spot.capacity,
            "no etag - same capacity",
        )

    def test_valid_json_valid_etag(self):
        new_name = "testing PUT name: {0}".format(random.random())
        new_capacity = 20

        spot_json = utils_test.get_spot(new_name, new_capacity)

        response = self.put_spot(self.url, spot_json)

        self.assertEqual(response.status_code, 200)

        updated_spot = Spot.objects.get(pk=self.spot.pk)
        self.assertEqual(updated_spot.name, new_name)
        self.assertEqual(updated_spot.capacity, new_capacity)

    def test_valid_json_outdated_etag(self):
        new_name = "testing PUT name: {0}".format(random.random())
        new_capacity = 30

        etag = self.get_etag(self.url)

        spot_json = utils_test.get_spot(new_name, new_capacity)

        intermediate_spot = Spot.objects.get(pk=self.spot.pk)
        intermediate_spot.name = "This interferes w/ the PUT"
        intermediate_spot.save()

        response = self.client.put(
            self.url, spot_json, content_type="application/json", If_Match=etag
        )

        self.assertEqual(
            response.status_code, 409, "An outdated etag leads to a conflict"
        )

        updated_spot = Spot.objects.get(pk=self.spot.pk)
        self.assertEqual(updated_spot.name, intermediate_spot.name)
        self.assertEqual(updated_spot.capacity, intermediate_spot.capacity)

    def test_no_duplicate_extended_info(self):
        new_name = "testing PUT name: {0}".format(random.random())
        new_capacity = 30

        spot_json = utils_test.get_spot(new_name, new_capacity)

        spot_json["extended_info"]["has_a_funky_beat"] = "true"

        self.put_spot(self.url, spot_json)

        self.put_spot(self.url, spot_json)

        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(key="has_a_funky_beat")),
            1,
        )

        spot_json["extended_info"]["has_a_funky_beat"] = "of_course"

        self.put_spot(self.url, spot_json)

        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(key="has_a_funky_beat")),
            1,
        )

        self.assertEqual(
            self.spot.spotextendedinfo_set.get(key="has_a_funky_beat").value,
            "of_course",
        )

    def test_deleted_spot_info(self):
        c = Client()
        new_name = "testing PUT name: {0}".format(random.random())
        new_capacity = 30

        etag = self.get_etag(self.url)
        response = c.put(
            self.url,
            '{"name":"%s","capacity":"%d", "location": '
            '{"latitude": 55, "longitude": 30}, '
            '"extended_info": {"eats_corn_pops": "true", '
            '"rages_hard": "true", "a": "true", "b": "true", '
            '"c": "true", "d": "true"} }' % (new_name, new_capacity),
            content_type="application/json",
            If_Match=etag,
        )

        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(key="eats_corn_pops")), 1
        )
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(key="rages_hard")), 1
        )
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(key="a")), 1
        )
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(key="b")), 1
        )

        etag = self.get_etag(self.url)
        response = c.put(
            self.url,
            '{"name":"%s","capacity":"%d", "location": '
            '{"latitude": 55, "longitude": 30}, '
            '"extended_info": {"eats_corn_pops": "true"} }'
            % (new_name, new_capacity),
            content_type="application/json",
            If_Match=etag,
        )

        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(key="eats_corn_pops")), 1
        )
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(key="rages_hard")), 0
        )
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(key="a")), 0
        )
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(key="b")), 0
        )

        etag = self.get_etag(self.url)
        response = c.put(
            self.url,
            '{"name":"%s","capacity":"%d", "location": '
            '{"latitude": 55, "longitude": 30} }' % (new_name, new_capacity),
            content_type="application/json",
            If_Match=etag,
        )

        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(key="eats_corn_pops")), 0
        )
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(key="rages_hard")), 0
        )
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(key="a")), 0
        )
        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(key="b")), 0
        )

        etag = self.get_etag(self.url)
        response = c.put(
            self.url,
            '{"name":"%s","capacity":"%d", "location": '
            '{"latitude": 55, "longitude": 30} }' % (new_name, new_capacity),
            content_type="application/json",
            If_Match=etag,
        )

        self.assertEqual(
            len(self.spot.spotextendedinfo_set.filter(key="eats_corn_pops")), 0
        )

        etag = self.get_etag(self.url)
        response = c.put(
            self.url,
            '{"name":"%s","capacity":"%d", "manager":"Yoda", '
            '"location": {"latitude": 55, "longitude": 30, '
            '"building_name": "Coruscant"} }' % (new_name, new_capacity),
            content_type="application/json",
            If_Match=etag,
        )

        self.assertEqual(len(Spot.objects.get(name=new_name).manager), 4)
        self.assertEqual(len(Spot.objects.get(name=new_name).building_name), 9)

        etag = self.get_etag(self.url)
        response = c.put(
            self.url,
            '{"name":"%s","capacity":"%d", "location": '
            '{"latitude": 55, "longitude": 30} }' % (new_name, new_capacity),
            content_type="application/json",
            If_Match=etag,
        )

        self.assertEqual(len(Spot.objects.get(name=new_name).manager), 0)
        self.assertEqual(len(Spot.objects.get(name=new_name).building_name), 0)

    def test_extended_info(self):
        c = Client()
        new_name = "testing PUT name: {0}".format(random.random())
        new_capacity = 20
        json_string = (
            '{"name":"%s","capacity":"%s", "location": '
            '{"latitude": 55, "longitude": 30}, '
            '"extended_info":{"has_outlets":"true"}}'
            % (new_name, new_capacity)
        )
        etag = self.get_etag(self.url)
        response = c.put(
            self.url,
            json_string,
            content_type="application/json",
            If_Match=etag,
        )
        spot_json = json.loads(response.content)
        extended_info = {"has_outlets": "true"}
        self.assertEqual(spot_json["extended_info"], extended_info)

    def test_new_extended_info(self):
        c = Client()
        name1 = "testing POST name: %s" % random.random()
        name2 = "testing POST name: %s" % random.random()
        name3 = "testing POST name: %s" % random.random()
        json_string1 = (
            '{"name":"%s","capacity":"10", "location": '
            '{"latitude": 50, "longitude": -30},'
            '"extended_info":{"has_whiteboards":"true", '
            '"has_printing":"true", "has_displays":"true", '
            '"num_computers":"38", "has_natural_light":'
            '"true"}}' % name1
        )
        response1 = c.post(
            "/api/v1/spot/",
            json_string1,
            content_type="application/json",
            follow=False,
        )
        json_string2 = (
            '{"name":"%s","capacity":"10", "location": '
            '{"latitude": 50, "longitude": -30},'
            '"extended_info":{"has_outlets":"true", '
            '"has_outlets":"true", "has_scanner":"true", '
            '"has_projector":"true", "has_computers":"true"}}' % name2
        )
        response2 = c.post(
            "/api/v1/spot/",
            json_string2,
            content_type="application/json",
            follow=False,
        )
        json_string3 = (
            '{"name":"%s","capacity":"10", "location": '
            '{"latitude": 50, "longitude": -30},'
            '"extended_info":{"has_outlets":"true", '
            '"has_printing":"true", "has_projector":"true", '
            '"num_computers":"15", "has_computers":"true", '
            '"has_natural_light":"true"}}' % name3
        )
        response3 = c.post(
            "/api/v1/spot/",
            json_string3,
            content_type="application/json",
            follow=False,
        )

        url1 = response1["Location"]
        url2 = response2["Location"]
        url3 = response3["Location"]

        # get etags
        etag1 = self.get_etag(url1)
        etag2 = self.get_etag(url2)
        etag3 = self.get_etag(url3)

        new_json_string1 = (
            '{"name":"%s","capacity":"10", "location": '
            '{"latitude": 50, "longitude": -30},'
            '"extended_info":{"has_whiteboards":"true", '
            '"something_new":"true", "has_printing":'
            '"true", "has_displays":"true", '
            '"num_computers":"38", "has_natural_light":'
            '"true"}}' % name1
        )
        new_json_string2 = (
            '{"name":"%s","capacity":"10", "location": '
            '{"latitude": 50, "longitude": -30},'
            '"extended_info":{"has_outlets":"true", '
            '"has_outlets":"true", "has_scanner":"true", '
            '"has_projector":"true", "has_computers":'
            '"true", "another_new":"yep it is"}}' % name2
        )
        new_json_string3 = (
            '{"name":"%s","capacity":"10", "location": '
            '{"latitude": 50, "longitude": -30},'
            '"extended_info":{"also_new":"ok", '
            '"another_new":"bleh", "has_outlets":"true", '
            '"has_printing":"true", "has_projector":'
            '"true", "num_computers":"15", '
            '"has_computers":"true", "has_natural_light":'
            '"true"}}' % name3
        )

        response = c.put(
            url1,
            new_json_string1,
            content_type="application/json",
            If_Match=etag1,
        )
        response = c.put(
            url2,
            new_json_string2,
            content_type="application/json",
            If_Match=etag2,
        )
        response = c.put(
            url3,
            new_json_string3,
            content_type="application/json",
            If_Match=etag3,
        )

        new_response1 = c.get(url1)
        spot_json1 = json.loads(new_response1.content)
        new_response2 = c.get(url2)
        spot_json2 = json.loads(new_response2.content)
        new_response3 = c.get(url3)
        spot_json3 = json.loads(new_response3.content)

        self.assertEqual(
            spot_json1["extended_info"],
            json.loads(new_json_string1)["extended_info"],
        )
        self.assertContains(new_response1, '"something_new": "true"')
        self.assertEqual(
            spot_json2["extended_info"],
            json.loads(new_json_string2)["extended_info"],
        )
        self.assertContains(new_response2, '"another_new": "yep it is"')
        self.assertEqual(
            spot_json3["extended_info"],
            json.loads(new_json_string3)["extended_info"],
        )
        self.assertContains(new_response3, '"also_new": "ok"')
        self.assertContains(new_response3, '"another_new": "bleh"')

    def test_update_spot_with_items(self):
        """Creates a spot and then updates it with items."""
        spot_name = self.random_name()
        capacity = 20

        spot_json = utils_test.get_spot(spot_name, capacity)

        for i in range(0, 10):
            spot_json["items"].append(utils_test.get_item())

        response = self.put_spot(self.url, spot_json)

        self.assertEqual(response.status_code, 200)

        try:
            updated_items = Item.objects.filter(spot=self.spot)
        except Exception as ex:
            self.fail("Items shoud exist but do not! :" + str(ex))

        self.assertEqual(len(updated_items), 10)

        for i in range(0, len(updated_items)):
            self.assertEqual(
                updated_items[i].json_data_structure()["name"],
                spot_json["items"][i]["name"],
            )
            self.assertEqual(
                updated_items[i].json_data_structure()["category"],
                spot_json["items"][i]["category"],
            )
            self.assertEqual(
                updated_items[i].json_data_structure()["subcategory"],
                spot_json["items"][i]["subcategory"],
            )

    def test_update_spot_with_missing_data(self):
        """
        Tests to make sure that updating a spot without all required fields
        fails, giving a 400.
        """
        spot_name = self.random_name()
        capacity = 20

        spot_json = utils_test.get_spot(spot_name, capacity)
        spot_json["items"].append(utils_test.get_item())

        new_spots = (
            copy.deepcopy(spot_json),
            copy.deepcopy(spot_json),
            copy.deepcopy(spot_json),
        )

        messages = (
            "Item name validation failed to raise an error",
            "Item category validation failed to raise an error",
            "Item subcategory validation failed to raise an error",
        )

        # delete required fields
        del new_spots[0]["items"][0]["name"]
        del new_spots[1]["items"][0]["category"]
        del new_spots[2]["items"][0]["subcategory"]

        for spot, message in zip(new_spots, messages):
            response = self.put_spot(self.url, spot)
            self.assertEqual(response.status_code, 400, message)

    def test_update_item_extended_info(self):
        """Test that item EI updates correctly."""
        ei = {
            "make_model": "itemmodel",
            "customer_type": "UW Student",
            "auto_item_status": "active",
        }

        spot_json = utils_test.get_spot(self.random_name(), 20)

        spot_json["items"].append(utils_test.get_item())

        for key, value in ei.items():
            spot_json["items"][0]["extended_info"][key] = value

        response = self.put_spot(self.url, spot_json)

        self.assertEqual(response.status_code, 200)

        get_response = self.client.get(self.url)

        spot_json = json.loads(get_response.content)

        self.assertEqual(len(spot_json["items"]), 1)

        self.assertIn(
            "extended_info",
            spot_json["items"][0],
            "No extended_info in the item!",
        )

        # assert that values were correct
        for key, value in ei.items():
            self.assertTrue(
                key in spot_json["items"][0]["extended_info"],
                key + " not in item extended info!",
            )

            self.assertEqual(
                spot_json["items"][0]["extended_info"][key],
                value,
                key
                + " was not "
                + value
                + ", was :"
                + spot_json["items"][0]["extended_info"][key],
            )

        spot_json["items"][0]["extended_info"]["make_model"] = "new_model"
        ei["make_model"] = "new_model"

        response = self.put_spot(self.url, spot_json)

        self.assertEqual(response.status_code, 200)

        get_response = self.client.get(self.url)

        spot_json = json.loads(get_response.content)

        self.assertEqual(len(spot_json["items"]), 1)

        self.assertIn(
            "extended_info",
            spot_json["items"][0],
            "No extended_info in the item!",
        )

        # assert that values were correct
        for key, value in ei.items():
            self.assertTrue(
                key in spot_json["items"][0]["extended_info"],
                key + " not in item extended info!",
            )

            self.assertEqual(
                spot_json["items"][0]["extended_info"][key],
                value,
                key
                + " was not "
                + value
                + ", was :"
                + spot_json["items"][0]["extended_info"][key],
            )

    def test_remove_item(self):
        """Tests to ensure that not including an item in PUT will remove it"""
        spot_name = self.random_name()
        capacity = 20

        spot_json = utils_test.get_spot(spot_name, capacity)

        for i in range(0, 10):
            spot_json["items"].append(utils_test.get_item())

        response = self.put_spot(self.url, spot_json)

        self.assertEqual(response.status_code, 200)

        del spot_json["items"][9]

        response = self.put_spot(self.url, spot_json)

        self.assertEqual(response.status_code, 200)

        try:
            updated_items = Item.objects.filter(spot=self.spot)
        except Exception as ex:
            self.fail("Items shoud exist but do not! :" + str(ex))

        self.assertEqual(len(updated_items), 9)

    def test_remove_item_extended_info(self):
        """Tests to ensure that not including an item EI in PUT will delete"""
        ei = {
            "make_model": "itemmodel",
            "customer_type": "UW Student",
            "auto_item_status": "active",
        }

        spot_json = utils_test.get_spot(self.random_name(), 20)

        spot_json["items"].append(utils_test.get_item())

        for key, value in ei.items():
            spot_json["items"][0]["extended_info"][key] = value

        response = self.put_spot(self.url, spot_json)

        spot_json = json.loads(response.content)

        self.assertEqual(response.status_code, 200)

        del spot_json["items"][0]["extended_info"]["make_model"]

        response = self.put_spot(self.url, spot_json)

        self.assertEqual(response.status_code, 200)

        get_response = self.client.get(self.url)

        updated_spot_json = json.loads(get_response.content)

        self.assertNotIn(
            "make_model", updated_spot_json["items"][0]["extended_info"]
        )

    def test_update_spot_items(self):
        """
        Tests that when a spot item is updated that changes persist and that
        the id remains the same.
        """
        spot_json = utils_test.get_spot(self.random_name(), 20)

        spot_json["items"].append(utils_test.get_item())

        response = self.put_spot(self.url, spot_json)

        get_response = self.client.get(self.url)

        returned_spot_json = json.loads(get_response.content)

        returned_spot_json["items"][0]["name"] = "Test!"

        response = self.put_spot(self.url, returned_spot_json)

        get_response = self.client.get(self.url)

        updated_spot_json = json.loads(get_response.content)

        self.assertEqual(
            updated_spot_json["items"][0]["id"],
            returned_spot_json["items"][0]["id"],
            "IDs do not match for updated spot!",
        )

        self.assertEqual(
            updated_spot_json["items"][0]["name"],
            returned_spot_json["items"][0]["name"],
            "Spot name failed to update!",
        )
