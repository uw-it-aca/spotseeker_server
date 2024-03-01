# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TransactionTestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot, SpotExtendedInfo
import simplejson as json
import random
from django.test.utils import override_settings
from mock import patch
from spotseeker_server import models
from spotseeker_server.test import utils_test

from past.builtins import basestring

ALL_OK = "spotseeker_server.auth.all_ok"
UW_SPOT_FORM = "spotseeker_server.org_forms.uw_spot.UWSpotForm"
UW_EXT_INFO_FORM = "spotseeker_server.org_forms.uw_spot.UWSpotExtendedInfoForm"


@override_settings(SPOTSEEKER_AUTH_MODULE=ALL_OK)
@override_settings(SPOTSEEKER_SPOT_FORM=UW_SPOT_FORM)
@override_settings(SPOTSEEKER_SPOTEXTENDEDINFO_FORM=UW_EXT_INFO_FORM)
@override_settings(SPOTSEEKER_AUTH_ADMINS=("demo_user",))
class UWSpotPUTTest(TransactionTestCase):
    """Tests updating Spot information via PUT."""

    def setUp(self):
        spot = Spot.objects.create(name="This is for testing PUT")
        SpotExtendedInfo.objects.create(
            spot=spot, key="aw_yisss", value="breadcrumbs"
        )
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
        c = Client()
        response = c.put(
            self.url,
            "this is just text",
            content_type="application/json",
            If_Match=self.spot.etag,
        )
        self.assertEquals(response.status_code, 400, "Rejects non-json")

    def test_invalid_url(self):
        c = Client()
        response = c.put(
            "/api/v1/spot/aa", "{}", content_type="application/json"
        )
        self.assertEquals(
            response.status_code, 404, "Rejects a non-numeric url"
        )

    def test_invalid_id_too_high(self):
        c = Client()
        test_id = self.spot.pk + 10000
        test_url = "/api/v1/spot/{0}".format(test_id)
        response = c.put(test_url, "{}", content_type="application/json")
        self.assertEquals(
            response.status_code,
            404,
            "Rejects an id that doesn't exist yet (no PUT to" "create)",
        )

    def test_empty_json(self):
        c = Client()
        response = c.put(
            self.url,
            "{}",
            content_type="application/json",
            If_Match=self.spot.etag,
        )
        self.assertEquals(response.status_code, 400, "Rejects an empty body")

    def test_valid_json_no_etag(self):
        c = Client()
        new_name = "testing PUT name: {0}".format(random.random())
        new_capacity = 10
        response = c.put(
            self.url,
            '{{"name":"{0}","capacity":"{1}"}}'.format(new_name, new_capacity),
            content_type="application/json",
        )
        self.assertEquals(response.status_code, 400, "Bad request w/o an etag")

        updated_spot = Spot.objects.get(pk=self.spot.pk)
        self.assertEquals(
            updated_spot.name, self.spot.name, "No etag - same name"
        )
        self.assertEquals(
            updated_spot.capacity,
            self.spot.capacity,
            "no etag - same capacity",
        )

    def test_valid_json_valid_etag(self):
        c = Client()
        new_name = "testing PUT name: {0}".format(random.random())
        new_capacity = 20

        response = c.get(self.url)
        etag = response["ETag"]

        json_string = (
            '{"name":"%s","capacity":"%s","location": \
            {"latitude": 55, "longitude": -30},"extended_info": \
            {"has_whiteboards":"true","has_outlets":"true", \
            "manager":"Sam","organization":"UW"}}'
            % (new_name, new_capacity)
        )
        response = c.put(
            self.url,
            json_string,
            content_type="application/json",
            If_Match=etag,
        )
        self.assertEquals(
            response.status_code, 200, "Accepts a valid json string"
        )

        updated_spot = Spot.objects.get(pk=self.spot.pk)
        self.assertEquals(
            updated_spot.name, new_name, "a valid PUT changes the name"
        )
        self.assertEquals(
            updated_spot.capacity,
            new_capacity,
            "a valid PUT changes the capacity",
        )

    def test_valid_json_outdated_etag(self):
        c = Client()
        new_name = "testing PUT name: {0}".format(random.random())
        new_capacity = 30

        response = c.get(self.url)
        etag = response["ETag"]

        intermediate_spot = Spot.objects.get(pk=self.spot.pk)
        intermediate_spot.name = "This interferes w/ the PUT"
        intermediate_spot.save()

        response = c.put(
            self.url,
            '{{"name":"{0}","capacity":"{1}"}}'.format(new_name, new_capacity),
            content_type="application/json",
            If_Match=etag,
        )
        self.assertEquals(
            response.status_code, 409, "An outdated etag leads to a conflict"
        )

        updated_spot = Spot.objects.get(pk=self.spot.pk)
        self.assertEquals(
            updated_spot.name,
            intermediate_spot.name,
            "keep the intermediate name w/ an outdated etag",
        )

    def test_valid_json_but_invalid_extended_info(self):
        with self.settings(
            SPOTSEEKER_AUTH_MODULE=ALL_OK, SPOTSEEKER_SPOT_FORM=UW_SPOT_FORM
        ):
            c = Client()
            new_name = "testing PUT name: {0}".format(random.random())
            new_capacity = 20

            response = c.get(self.url)
            etag = response["ETag"]
            app_type = "food"

            json_string = (
                '{"name":"%s","capacity":"%s",\
                "location":{"latitude": 55, "longitude": -30},\
                "extended_info":{"location_description":\
                "This is a description",\
                "has_whiteboards":"true",\
                "num_computers": "10",\
                "has_outlets":"true","has_computers":"true",\
                "manager":"Sam","organization":"UW",\
                "app_type":"%s"}}'
                % (new_name, new_capacity, app_type)
            )

            response = c.put(
                self.url,
                json_string,
                content_type="application/json",
                If_Match=etag,
            )
            self.assertEquals(
                response.status_code, 200, "Accepts a valid json string"
            )

            # test: invalid extended info value
            response = c.get(self.url)
            etag = response["ETag"]
            updated_json_string = (
                '{"name":"%s","capacity":"%s",\
                "location": {"latitude": 55, "longitude": -30},\
                "extended_info":{"has_whiteboards":"true",\
                "location_description": "   ",\
                "has_outlets":"wub wub wub wu wu wuhhhh WUB WUB WUBBBBUB", \
                "has_computers":"true", "num_computers":"10","manager":"Sam",\
                "organization":"UW"}}'
                % (new_name, new_capacity)
            )

            response = c.put(
                self.url,
                updated_json_string,
                content_type="application/json",
                If_Match=etag,
            )
            self.assertEquals(
                response.status_code,
                400,
                "Doesn't update spot with invalid extended info",
            )

            response = c.get(self.url)
            self.assertEquals(
                json.loads(json_string)["extended_info"],
                json.loads(response.content)["extended_info"],
                "Doesn't update spot with invalid extended info",
            )

            # test: invalid int value
            invalid_int = "invalid_int"
            invalid_int_json_string = (
                '{"name":"%s","capacity":"%s",\
                "location": {"latitude": 55, "longitude": -30},\
                "extended_info":{"has_whiteboards":"true",\
                "location_description": "This is a description",\
                "has_outlets":"true", "has_computers":"true", \
                "num_computers":"%s","manager":"Sam","organization":"UW"}}'
                % (new_name, new_capacity, invalid_int)
            )

            response = c.put(
                self.url,
                invalid_int_json_string,
                content_type="application/json",
                If_Match=etag,
            )
            self.assertEquals(
                response.status_code,
                400,
                "Doesn't update spot with invalid int value",
            )

            response = c.get(self.url)
            self.assertEquals(
                json.loads(json_string)["extended_info"],
                json.loads(response.content)["extended_info"],
                "Doesn't update spot with invalid int value",
            )

    def test_phone_number_validation(self):
        phone_numbers = (
            "(425) 274-2853",
            "(206) 285-2884",
            "206 203 3829",
            "206.211.2495",
            "(253) 284-2848",
            "(204)-203 2848",
            "13235659898",  # with country code
            "+1 234 234 2345",
        )

        formatted_phone_numbers = (
            "4252742853",
            "2062852884",
            "2062033829",
            "2062112495",
            "2532842848",
            "2042032848",
            "3235659898",
            "2342342345",
            "2455463232",
        )

        spot_json = utils_test.get_spot("Test name", 20)

        spot_json["extended_info"]["test_ei"] = "ei"

        response = self.put_spot(self.url, spot_json)

        self.assertEqual(response.status_code, 200)

        spot_json = json.loads(response.content)

        for number, formatted_number in zip(
            phone_numbers, formatted_phone_numbers
        ):
            spot_json["extended_info"]["s_phone"] = number

            response = self.put_spot(self.url, spot_json)

            self.assertEqual(
                response.status_code,
                200,
                'Good phone number "%s" was rejected' % number,
            )

            spot_json = json.loads(response.content)

            self.assertEqual(
                spot_json["extended_info"]["s_phone"], formatted_number
            )

        last_good_number = formatted_number

    def test_phone_numbers_invalid(self):

        good_phone_number = "4252742853"

        bad_phone_numbers = (
            "123456789",  # not enough digits
            "This is not a phone number",  # letters
            "23423423423499999999999",  # too many digits
            "121-343-5656 (office)",  # Extra stuff
            "For reservations, call 245-546-3232",
            "2942033829",  # Nonexistent area code
        )

        spot_json = utils_test.get_spot("Test name", 20)
        spot_json["extended_info"]["test_ei"] = "ei"

        response = self.put_spot(self.url, spot_json)
        response_json = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        spot_json = json.loads(response.content)

        spot_json["extended_info"]["s_phone"] = good_phone_number
        response = self.put_spot(self.url, spot_json)

        self.assertEqual(
            response.status_code,
            200,
            "Test prep failed, couldn't add valid phone #",
        )

        spot_json = json.loads(response.content)
        self.assertEqual(
            spot_json["extended_info"]["s_phone"], good_phone_number
        )

        for number in bad_phone_numbers:
            spot_json["extended_info"]["s_phone"] = number
            response = self.put_spot(self.url, spot_json)
            self.assertEqual(
                response.status_code,
                400,
                'Bad phone number "%s" was accepted' % number,
            )
            new_spot_json = json.loads(self.client.get(self.url).content)
            self.assertEqual(
                new_spot_json["extended_info"]["s_phone"],
                good_phone_number,
                "Expected phone to not change after PUTing bad "
                "number %s" % number,
            )
