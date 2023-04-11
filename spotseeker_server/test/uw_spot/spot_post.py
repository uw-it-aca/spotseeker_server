# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TransactionTestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot
import simplejson as json
import random
from django.test.utils import override_settings
from mock import patch
from spotseeker_server import models


ALL_OK = "spotseeker_server.auth.all_ok"
UW_SPOT_FORM = "spotseeker_server.org_forms.uw_spot.UWSpotForm"
UW_EXT_INFO_FORM = "spotseeker_server.org_forms.uw_spot.UWSpotExtendedInfoForm"


@override_settings(SPOTSEEKER_AUTH_MODULE=ALL_OK)
@override_settings(SPOTSEEKER_SPOT_FORM=UW_SPOT_FORM)
@override_settings(SPOTSEEKER_SPOTEXTENDEDINFO_FORM=UW_EXT_INFO_FORM)
@override_settings(SPOTSEEKER_AUTH_ADMINS=("demo_user",))
class UWSpotPOSTTest(TransactionTestCase):
    """Tests creating a new Spot via POST."""

    def test_valid_json(self):
        c = Client()
        new_name = "Testing POST Name: {0}".format(random.random())
        new_capacity = 10
        json_string = (
            '{"name":"%s","capacity":"%s",\
            "location":{"latitude": 55, "longitude": -30},\
            "extended_info":{"has_whiteboards":"true",\
            "has_outlets":"true","manager":"Bob",\
            "organization":"UW"}}'
            % (new_name, new_capacity)
        )
        response = c.post(
            "/api/v1/spot/",
            json_string,
            content_type="application/json",
            follow=False,
        )
        self.assertEquals(
            response.status_code,
            201,
            "Gives a Created response to creating a Spot",
        )
        self.assertIn(
            "Location", response, "The response has a location header"
        )

        self.spot = Spot.objects.get(name=new_name)

        self.assertEquals(
            response["Location"],
            self.spot.rest_url(),
            "The url for the new spot is correct",
        )

        get_response = c.get(response["Location"])
        self.assertEquals(
            get_response.status_code,
            200,
            "OK in response to GETing the new spot",
        )

        spot_json = json.loads(get_response.content)

        self.assertEquals(
            spot_json["name"], new_name, "The right name was stored"
        )
        self.assertEquals(
            spot_json["capacity"],
            new_capacity,
            "The right capacity was stored",
        )

    def test_non_json(self):
        c = Client()
        response = c.post(
            "/api/v1/spot/",
            "just a string",
            content_type="application/json",
            follow=False,
        )
        self.assertEquals(response.status_code, 400)

    def test_invalid_json(self):
        c = Client()
        response = c.post(
            "/api/v1/spot/",
            "{}",
            content_type="application/json",
            follow=False,
        )
        self.assertEquals(response.status_code, 400)

    def uw_ei_field_common(self, field, invalid_cases, valid_cases):
        """
        A common helper function to used by different tests. The field provided
        will be tested against. invalid_cases and valid_cases hold the list of
        test cases.
        """
        c = Client()
        new_name = "Testing POST Name: {0}".format(random.random())
        new_capacity = 10
        for invalid in invalid_cases:
            json_string = (
                '{"name":"%s","capacity":"%s","location":\
                {"latitude": 55, "longitude": -30},\
                "extended_info":{"%s":"%s","has_outlets":"true",\
                "manager":"John","organization":"UW"}}'
                % (new_name, new_capacity, field, invalid)
            )
            response = c.post(
                "/api/v1/spot/",
                json_string,
                content_type="application/json",
                follow=False,
            )
            self.assertEquals(
                response.status_code,
                400,
                (
                    "Spot not created: %s field did not pass"
                    " validation" % field
                ),
            )

        for valid in valid_cases:
            json_string = (
                '{"name":"%s","capacity":"%s","location":\
                {"latitude": 55, "longitude": -30},\
                "extended_info":{"%s":"%s","has_outlets":"true",\
                "manager":"John","organization":"UW"}}'
                % (new_name, new_capacity, field, valid)
            )
            response = c.post(
                "/api/v1/spot/",
                json_string,
                content_type="application/json",
                follow=False,
            )

            self.assertEquals(response.status_code, 201)

    def test_uw_field_labstats_id(self):
        field = "labstats_id"
        invalid_cases = ["One", "1One"]
        valid_cases = ["1"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_campus(self):
        field = "campus"
        invalid_cases = ["south_", "1"]
        valid_cases = ["south_lake_union", "seattle"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_auto_labstats_available(self):
        field = "auto_labstats_available"
        invalid_cases = ["One", "1One"]
        valid_cases = ["1"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_auto_labstats_total(self):
        field = "auto_labstats_total"
        invalid_cases = ["One", "1One"]
        valid_cases = ["1"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_has_whiteboards(self):
        field = "has_whiteboards"
        invalid_cases = ["true1", "10"]
        valid_cases = ["true"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_app_type(self):
        field = "app_type"
        invalid_cases = ["foo"]
        valid_cases = ["tech", "food"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_has_outlets(self):
        c = Client()
        new_name = "Testing POST Name: {0}".format(random.random())
        new_capacity = 10

        json_string = (
            '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_whiteboards":"false","manager":"Harry",\
            "organization":"UW"}}'
            % (new_name, new_capacity)
        )
        response = c.post(
            "/api/v1/spot/",
            json_string,
            content_type="application/json",
            follow=False,
        )
        self.assertEquals(
            response.status_code,
            400,
            "Spot not created: has_outlets was not included",
        )

        has_outlets = 21
        json_string = (
            '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_whiteboards":"false","has_outlets":"%s",\
            "manager":"Harry","organization":"UW"}}'
            % (new_name, new_capacity, has_outlets)
        )
        response = c.post(
            "/api/v1/spot/",
            json_string,
            content_type="application/json",
            follow=False,
        )
        self.assertEquals(
            response.status_code,
            400,
            ("Spot not created; has_outlets field did not pass validation"),
        )

        has_outlets = "true"
        json_string = (
            '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_whiteboards":"true","has_outlets":"%s",\
            "manager":"Harry","organization":"UW"}}'
            % (new_name, new_capacity, has_outlets)
        )
        response = c.post(
            "/api/v1/spot/",
            json_string,
            content_type="application/json",
            follow=False,
        )
        self.assertEquals(response.status_code, 201)

    def test_uw_field_has_printing(self):
        field = "has_printing"
        invalid_cases = ["12", "Nope"]
        valid_cases = ["true"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_has_scanner(self):
        field = "has_scanner"
        invalid_cases = ["10", "None here"]
        valid_cases = ["true"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_has_displays(self):
        field = "has_displays"
        invalid_cases = ["10", "Nope"]
        valid_cases = ["true"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_has_projector(self):
        field = "has_projector"
        invalid_cases = ["23", "Nope"]
        valid_cases = ["true"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_has_computers(self):
        field = "has_computers"
        invalid_cases = ["10", "Nope"]
        valid_cases = ["true"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_num_computers(self):
        field = "num_computers"
        invalid_cases = ["Invalid Data", "1One"]
        valid_cases = ["23"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_has_natural_light(self):
        field = "has_natural_light"
        invalid_cases = ["truer", "10"]
        valid_cases = ["true"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_noise_level(self):
        field = "noise_level"
        invalid_cases = ["silent sound"]
        valid_cases = ["moderate", "silent"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_food_nearby(self):
        field = "food_nearby"
        invalid_cases = ["building next door"]
        valid_cases = ["building", "space"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_reservable(self):
        field = "reservable"
        invalid_cases = ["0", "false"]
        valid_cases = ["true", "reservations"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_location_description(self):
        field = "location_description"
        invalid_cases = ["     ", "1232"]
        valid_cases = ["This is a valid description"]
        self.uw_ei_field_common(field, invalid_cases, valid_cases)

    def test_uw_field_matches_location_description(self):
        c = Client()
        new_name = "Testing POST Name: {0}".format(random.random())
        new_capacity = 10

        desc = "This is a description"
        json_string = (
            '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude":-30},\
            "extended_info":{"has_outlets":"true",\
            "location_description":"%s","manager":"Patty",\
            "organization":"UW"}}'
            % (new_name, new_capacity, desc)
        )
        response = c.post(
            "/api/v1/spot/",
            json_string,
            content_type="application/json",
            follow=False,
        )

        self.assertEquals(response.status_code, 201)

        spot = Spot.objects.get(name=new_name)
        spot_desc = spot.spotextendedinfo_set.get(
            key="location_description"
        ).value

        self.assertEquals(
            desc, spot_desc, "The spot description matches what was POSTed."
        )

    def test_valid_json_but_invalid_extended_info(self):
        c = Client()
        new_name = "Testing POST Name: {0}".format(random.random())
        new_capacity = 10

        json_string = (
            '{"name":"%s","capacity":\
            "%s","location": {"latitude": 55, "longitude":-30},\
            "extended_info":{"has_outlets":"true","manager":"Patty",\
            "organization":"UW"}}'
            % (new_name, new_capacity)
        )
        response = c.post(
            "/api/v1/spot/",
            json_string,
            content_type="application/json",
            follow=False,
        )
        self.assertEquals(response.status_code, 201)

        response = c.post(
            "/api/v1/spot/",
            json_string,
            content_type="application/json",
            follow=False,
        )
        bad_json_string = (
            '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_whiteboards":"true",\
            "has_outlets":"wub wub wub wu wu wuhhhh WUB WUB WUBBBBUB",\
            "manager":"Sam","organization":"UW"}}'
            % (new_name, new_capacity)
        )
        response = c.post(
            "/api/v1/spot/",
            bad_json_string,
            content_type="application/json",
            follow=False,
        )
        self.assertEquals(
            response.status_code,
            400,
            "Doesn't add spot info; invalid extended info",
        )
        self.assertEquals(
            Spot.objects.count(),
            2,
            "Doesn't POST spots with invalid extended info",
        )

    def test_valid_json_but_no_extended_info(self):
        c = Client()
        new_name = "Testing POST Name: {0}".format(random.random())
        new_cap = 10

        json_string = (
            '{"name":"%s","capacity":"%s", \
            "location": {"latitude": 55, "longitude":-30}}'
            % (new_name, new_cap)
        )
        response = c.post(
            "/api/v1/spot/",
            json_string,
            content_type="application/json",
            follow=False,
        )

        error_message = json.loads(
            json.loads(response.content)["error"]
            .replace("u'", '"')
            .replace("'", '"')
        )
        self.assertEquals(
            error_message,
            [u"UWSpot must have extended info"],
            "Doesn't add spot info; invalid extended info",
        )
