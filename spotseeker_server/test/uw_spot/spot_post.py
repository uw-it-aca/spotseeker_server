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

from django.test import TransactionTestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot
import simplejson as json
import random
from django.test.utils import override_settings
from mock import patch
from spotseeker_server import models


ALL_OK = 'spotseeker_server.auth.all_ok'
UW_SPOT_FORM = 'spotseeker_server.org_forms.uw_spot.UWSpotForm'
UW_EXT_INFO_FORM = 'spotseeker_server.org_forms.uw_spot.UWSpotExtendedInfoForm'


@override_settings(SPOTSEEKER_AUTH_MODULE=ALL_OK)
@override_settings(SPOTSEEKER_SPOT_FORM=UW_SPOT_FORM)
@override_settings(SPOTSEEKER_SPOTEXTENDEDINFO_FORM=UW_EXT_INFO_FORM)
@override_settings(SPOTSEEKER_AUTH_ADMINS=('demo_user',))
class UWSpotPOSTTest(TransactionTestCase):
    """ Tests creating a new Spot via POST.
    """

    def test_valid_json(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10
        json_string = '{"name":"%s","capacity":"%s",\
            "location":{"latitude": 55, "longitude": -30},\
            "extended_info":{"has_whiteboards":"true",\
            "has_outlets":"true","manager":"Bob",\
            "organization":"UW"}}' % (new_name, new_capacity)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 201,
                          "Gives a Created response to creating a Spot")
        self.assertIn("Location", response,
                      "The response has a location header")

        self.spot = Spot.objects.get(name=new_name)

        self.assertEquals(response["Location"],
                          "http://testserver" + self.spot.rest_url(),
                          "The uri for the new spot is correct")

        get_response = c.get(response["Location"])
        self.assertEquals(get_response.status_code, 200,
                          "OK in response to GETing the new spot")

        spot_json = json.loads(get_response.content)

        self.assertEquals(spot_json["name"], new_name,
                          "The right name was stored")
        self.assertEquals(spot_json["capacity"], new_capacity,
                          "The right capacity was stored")

    def test_non_json(self):
        c = Client()
        response = c.post('/api/v1/spot/', 'just a string',
                          content_type="application/json", follow=False)
        self.assertEquals(response.status_code, 400)

    def test_invalid_json(self):
        c = Client()
        response = c.post('/api/v1/spot/', '{}',
                          content_type="application/json", follow=False)
        self.assertEquals(response.status_code, 400)

    def test_uw_field_labstats_id(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10
        labstats_id = "One"
        json_string = '{"name":"%s","capacity":"%s","location":\
            {"latitude": 55, "longitude": -30},\
            "extended_info":{"labstats_id":"%s","has_outlets":"true",\
            "manager":"John","organization":"UW"}}' % (new_name,
                                                       new_capacity,
                                                       labstats_id)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 400,
                          ("Not created; has_whiteboards field did not "
                           "pass validation"))
        labstats_id = "1One"
        json_string = '{"name":"%s","capacity":"%s","location":\
            {"latitude": 55, "longitude": -30},\
            "extended_info":{"labstats_id":"%s","has_outlets":"true",\
            "manager":"John","organization":"UW"}}' % (new_name,
                                                       new_capacity,
                                                       labstats_id)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 400,
                          ("Not created; has_whiteboards field did not "
                           "pass validation"))

        labstats_id = "1"
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"labstats_id":"%s","has_outlets":"true",\
            "manager":"John","organization":"UW"}}' % (new_name,
                                                       new_capacity,
                                                       labstats_id)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 201,
                          "Gives a Created response to creating a Spot")
        labstats_id = 2
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"labstats_id":"%s","has_outlets":"true",\
            "manager":"John","organization":"UW"}}' % (new_name,
                                                       new_capacity,
                                                       labstats_id)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 201,
                          "Gives a Created response to creating a Spot")

    def test_uw_field_campus(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10

        campus_tests = {"Invalid Campus", "Broken", "south_"}
        for campus in campus_tests:
            json_string = '{"name":"%s","capacity":"%s","location":\
                {"latitude": 55, "longitude": -30},\
                "extended_info":{"campus":"%s","has_outlets":"true",\
                "manager":"John","organization":"UW"}}' % (new_name,
                                                           new_capacity,
                                                           campus)
            response = c.post('/api/v1/spot/', json_string,
                              content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400,
                              ("Not created; has_whiteboards field did not "
                               "pass validation"))

        campus_tests = {"south_lake_union", "seattle", "tacoma", "bothell"}
        for campus in campus_tests:
            json_string = '{"name":"%s","capacity":"%s","location":\
                {"latitude": 55, "longitude": -30},\
                "extended_info":{"campus":"%s","has_outlets":"true",\
                "manager":"John","organization":"UW"}}' % (new_name,
                                                           new_capacity,
                                                           campus)
            response = c.post('/api/v1/spot/', json_string,
                              content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201,
                              "Gives a Created response to creating a Spot")

    def test_uw_field_review_count(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10

        review_count_tests = {"One", "1One"}
        for review_count in review_count_tests:
            json_string = '{"name":"%s","capacity":"%s","location":\
                {"latitude": 55, "longitude": -30},\
                "extended_info":{"review_count":"%s","has_outlets":"true",\
                "manager":"John","organization":"UW"}}' % (new_name,
                                                           new_capacity,
                                                           review_count)
            response = c.post('/api/v1/spot/', json_string,
                              content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400,
                              ("Not created; has_whiteboards field did not "
                               "pass validation"))

        review_count_tests = {"1", 2}
        for review_count in review_count_tests:
            json_string = '{"name":"%s","capacity":"%s","location":\
                {"latitude": 55, "longitude": -30},\
                "extended_info":{"review_count":"%s","has_outlets":"true",\
                "manager":"John","organization":"UW"}}' % (new_name,
                                                           new_capacity,
                                                           review_count)
            response = c.post('/api/v1/spot/', json_string,
                              content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201,
                              "Gives a Created response to creating a Spot")

    def test_uw_field_rating(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10

        rating_tests = {"One", "1One"}
        for rating in rating_tests:
            json_string = '{"name":"%s","capacity":"%s","location":\
                {"latitude": 55, "longitude": -30},\
                "extended_info":{"rating":"%s","has_outlets":"true",\
                "manager":"John","organization":"UW"}}' % (new_name,
                                                           new_capacity,
                                                           rating)
            response = c.post('/api/v1/spot/', json_string,
                              content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400,
                              ("Not created; has_whiteboards field did not "
                               "pass validation"))

        rating_tests = {"1", 2}
        for rating in rating_tests:
            json_string = '{"name":"%s","capacity":"%s","location":\
                {"latitude": 55, "longitude": -30},\
                "extended_info":{"rating":"%s","has_outlets":"true",\
                "manager":"John","organization":"UW"}}' % (new_name,
                                                           new_capacity,
                                                           rating)
            response = c.post('/api/v1/spot/', json_string,
                              content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201,
                              "Gives a Created response to creating a Spot")

    def test_uw_field_auto_labstats_available(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10

        auto_labstats_available_tests = {"One", "1One"}
        for auto_labstats_avail in auto_labstats_available_tests:
            json_string = '{"name":"%s","capacity":"%s","location":\
                {"latitude": 55, "longitude": -30},\
                "extended_info":{"auto_labstats_available":"%s","has_outlets":"true",\
                "manager":"John","organization":"UW"}}' % (new_name,
                                                           new_capacity,
                                                           auto_labstats_avail)
            response = c.post('/api/v1/spot/', json_string,
                              content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400,
                              ("Not created; has_whiteboards field did not "
                               "pass validation"))

        auto_labstats_available_tests = {"1", 2}
        for auto_labstats_avail in auto_labstats_available_tests:
            json_string = '{"name":"%s","capacity":"%s","location":\
                {"latitude": 55, "longitude": -30},\
                "extended_info":{"auto_labstats_available":"%s","has_outlets":"true",\
                "manager":"John","organization":"UW"}}' % (new_name,
                                                           new_capacity,
                                                           auto_labstats_avail)
            response = c.post('/api/v1/spot/', json_string,
                              content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201,
                              "Gives a Created response to creating a Spot")

    def test_uw_field_auto_labstats_total(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10
        auto_labstats_total_tests = {"One", "1One"}
        for auto_labstats_total in auto_labstats_total_tests:
            json_string = '{"name":"%s","capacity":"%s","location":\
                {"latitude": 55, "longitude": -30},\
                "extended_info":{"auto_labstats_total":"%s","has_outlets":"true",\
                "manager":"John","organization":"UW"}}' % (new_name,
                                                           new_capacity,
                                                           auto_labstats_total)
            response = c.post('/api/v1/spot/', json_string,
                              content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400,
                              ("Not created; has_whiteboards field did not "
                               "pass validation"))

        auto_labstats_total_tests = {"1", 2}
        for auto_labstats_total in auto_labstats_total_tests:
            json_string = '{"name":"%s","capacity":"%s","location":\
                {"latitude": 55, "longitude": -30},\
                "extended_info":{"auto_labstats_total":"%s","has_outlets":"true",\
                "manager":"John","organization":"UW"}}' % (new_name,
                                                           new_capacity,
                                                           auto_labstats_total)
            response = c.post('/api/v1/spot/', json_string,
                              content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201,
                              "Gives a Created response to creating a Spot")

    def test_uw_field_has_whiteboards(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10
        whiteboards = 12
        json_string = '{"name":"%s","capacity":"%s","location":\
            {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_whiteboards":"%s","has_outlets":"true",\
            "manager":"John","organization":"UW"}}' % (new_name,
                                                       new_capacity,
                                                       whiteboards)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 400,
                          ("Not created; has_whiteboards field did not "
                           "pass validation"))

        whiteboards = 'true'
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_whiteboards":"%s","has_outlets":"true",\
            "manager":"John","organization":"UW"}}' % (new_name,
                                                       new_capacity,
                                                       whiteboards)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 201,
                          "Gives a Created response to creating a Spot")

    def test_uw_field_app_type(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        app_type_tests = {"foo", "Invalid Data"}
        for app_type in app_type_tests:
            json_string = '{"name":"%s","capacity":"10",\
                "location": {"latitude": 55, "longitude": -30},\
                "extended_info":{"has_whiteboards":"true",\
                "has_outlets":"true","manager":"John","organization":"UW",\
                "app_type":"%s"}}' % (new_name, app_type)

            response = c.post('/api/v1/spot/', json_string,
                              content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400)

        app_type_tests = {"food", "tech"}
        for app_type in app_type_tests:
            json_string = '{"name":"%s","capacity":"10",\
                "location": {"latitude": 55, "longitude": -30},\
                "extended_info":{"has_whiteboards":"true",\
                "has_outlets":"true","manager":"John","organization":"UW",\
                "app_type":"%s"}}' % (new_name, app_type)

            response = c.post('/api/v1/spot/', json_string,
                              content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201)

    def test_uw_field_has_outlets(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10
        outlets = 12

        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_whiteboards":"false","manager":"Harry",\
            "organization":"UW"}}' % (new_name, new_capacity)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)
        self.assertEquals(response.status_code, 400,
                          "Not created; has_outlets was not included")

        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_whiteboards":"false","has_outlets":"%s",\
            "manager":"Harry","organization":"UW"}}' % (new_name,
                                                        new_capacity,
                                                        outlets)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)
        self.assertEquals(response.status_code, 400,
                          ("Not created; has_outlets field did not pass "
                           "validation"))

        outlets = 'true'
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_whiteboards":"true","has_outlets":"%s",\
            "manager":"Harry","organization":"UW"}}' % (new_name,
                                                        new_capacity,
                                                        outlets)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)
        self.assertEquals(response.status_code, 201,
                          "Gives a Created response to creating a Spot")

    def test_uw_field_has_printing(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10
        printer = 12
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_outlets":"true","has_printing":"%s",\
            "manager":"Gary","organization":"UW"}}' % (new_name,
                                                       new_capacity,
                                                       printer)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 400,
                          ("Not created; has_printing field did not pass "
                           "validation"))

        printer = 'true'
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_outlets":"true","has_printing":"%s",\
            "manager":"Gary","organization":"UW"}}' % (new_name,
                                                       new_capacity,
                                                       printer)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 201,
                          "Gives a Created response to creating a Spot")

    def test_uw_field_has_scanner(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10
        scanner = 'There are none'
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_outlets":"true","has_scanner":"%s",\
            "manager":"Sally","organization":"UW"}}' % (new_name,
                                                        new_capacity,
                                                        scanner)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 400,
                          ("Not created; has_scanner field did not pass "
                           "validation"))

        scanner = 'true'
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_outlets":"true","has_scanner":"%s",\
            "manager":"Sally","organization":"UW"}}' % (new_name,
                                                        new_capacity,
                                                        scanner)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 201,
                          "Gives a Created response to creating a Spot")

    def test_uw_field_has_displays(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10
        has_displays = 'There are none'
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_outlets":"true","has_displays":"%s",\
            "manager":"Fred","organization":"UW"}}' % (new_name,
                                                       new_capacity,
                                                       has_displays)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 400,
                          ("Not created; has_displays field did not pass "
                           "validation"))

        has_displays = 'true'
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_outlets":"true","has_displays":"%s",\
            "manager":"Fred","organization":"UW"}}' % (new_name,
                                                       new_capacity,
                                                       has_displays)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 201,
                          "Gives a Created response to creating a Spot")

    def test_uw_field_has_projector(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10
        has_projector = 'There are none'
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_outlets":"true","has_projector":"%s",\
            "manager":"George","organization":"UW"}}' % (new_name,
                                                         new_capacity,
                                                         has_projector)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 400,
                          ("Not created; has_projector field did not pass "
                           "validation"))

        has_projector = 'true'
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_outlets":"true","has_projector":"%s",\
            "manager":"George","organization":"UW"}}' % (new_name,
                                                         new_capacity,
                                                         has_projector)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 201,
                          "Gives a Created response to creating a Spot")

    def test_uw_field_has_computers(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10
        computers = 'There are none'
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_outlets":"true","has_computers":"%s",\
            "manager":"Tina","organization":"UW"}}' % (new_name,
                                                       new_capacity,
                                                       computers)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 400,
                          ("Not created; has_computers field did not pass "
                           "validation"))

        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_outlets":"true","has_computers":"true",\
            "manager":"Tina","organization":"UW"}}' % (new_name,
                                                       new_capacity)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 201,
                          "Gives a Created response to creating a Spot")

    def test_uw_field_num_computers(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10
        computers = "invalid_int"
        json_string = '{"name":"%s","capacity":"%s",\
            "location":{"latitude": 55, "longitude": -30},\
            "extended_info":{"has_outlets":"true","has_computers":"true",\
            "num_computers":"%s","manager":"Tina",\
            "organization":"UW"}}' % (new_name, new_capacity, computers)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)
        self.assertEquals(response.status_code, 400,
                          ("Make sure not to create the spot because "
                           "num_computers field did not pass validation"))

        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_outlets":"true","has_computers":"true",\
            "num_computers":"15","manager":"Tina",\
            "organization":"UW"}}' % (new_name, new_capacity)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 201,
                          "Gives a Created response to creating a Spot")

    def test_uw_field_has_natural_light(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10
        has_natural_light = 'Nope!'
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_outlets":"true",\
            "has_natural_light":"%s","manager":"Mary",\
            "organization":"UW"}}' % (new_name,
                                      new_capacity,
                                      has_natural_light)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 400,
                          ("Not created; has_natural_light field did not "
                           "pass validation"))

        has_natural_light = 'true'
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_outlets":"true",\
            "has_natural_light":"%s","manager":"Mary",\
            "organization":"UW"}}' % (new_name,
                                      new_capacity,
                                      has_natural_light)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 201,
                          "Gives a Created response to creating a Spot")

    def test_uw_field_noise_level(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10
        noise_level = 'Rock Concert'
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_outlets":"true","noise_level":"%s",\
            "manager":"Patty","organization":"UW"}}' % (new_name,
                                                        new_capacity,
                                                        noise_level)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 400,
                          ("Not created; noise_level field did not pass "
                           "validation"))

        noise_level_tests = {"moderate", "silent", "quiet", "variable"}
        for noise_level in noise_level_tests:
            json_string = '{"name":"%s","capacity":"%s",\
                "location": {"latitude": 55, "longitude": -30},\
                "extended_info":{"has_outlets":"true","noise_level":"%s",\
                "manager":"Patty","organization":"UW"}}' % (new_name,
                                                            new_capacity,
                                                            noise_level)
            response = c.post('/api/v1/spot/', json_string,
                              content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201,
                              "Gives a Created response to creating a Spot")

    def test_uw_field_food_nearby(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10
        food_nearby = 'In the area'
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_outlets":"true","food_nearby":"%s",\
            "manager":"Kristy","organization":"UW"}}' % (new_name,
                                                         new_capacity,
                                                         food_nearby)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 400,
                          ("Not created; food_nearby field did not pass "
                           "validation"))

        food_nearby_tests = {"building", "space", "neighboring"}
        for food_nearby in food_nearby_tests:
            json_string = '{"name":"%s","capacity":"%s",\
                "location": {"latitude": 55, "longitude": -30},\
                "extended_info":{"has_outlets":"true","food_nearby":"%s",\
                "manager":"Kristy","organization":"UW"}}' % (new_name,
                                                             new_capacity,
                                                             food_nearby)
            response = c.post('/api/v1/spot/', json_string,
                              content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201,
                              "Gives a Created response to creating a Spot")

    def test_uw_field_reservable(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10
        reservable_tests = {"You bet", "false"}
        for reservable in reservable_tests:
            json_string = '{"name":"%s","capacity":"%s",\
                "location": {"latitude": 55, "longitude": -30},\
                "extended_info":{"has_outlets":"true","reservable":"%s",\
                "manager":"Patty","organization":"UW"}}' % (new_name,
                                                            new_capacity,
                                                            reservable)
            response = c.post('/api/v1/spot/', json_string,
                              content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400,
                              ("Not created because reservable field did not "
                               "pass validation"))

        reservable_tests = {"reservations", "true"}
        for reservable in reservable_tests:
            json_string = '{"name":"%s","capacity":"%s",\
                "location": {"latitude": 55, "longitude": -30},\
                "extended_info":{"has_outlets":"true","reservable":"%s",\
                "manager":"Patty","organization":"UW"}}' % (new_name,
                                                            new_capacity,
                                                            reservable)
            response = c.post('/api/v1/spot/', json_string,
                              content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201,
                              "Gives a Created response to creating a Spot")

    def test_uw_field_location_description(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10

        desc = 'This is a description'
        json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude":-30},\
            "extended_info":{"has_outlets":"true",\
            "location_description":"%s","manager":"Patty",\
            "organization":"UW"}}' % (new_name, new_capacity, desc)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 201,
                          "Gives a Created response to creating a Spot")

        spot = Spot.objects.get(name=new_name)
        spot_desc = spot.spotextendedinfo_set.get(
            key='location_description').value

        self.assertEquals(desc, spot_desc,
                          "The Spot description matches what was POSTed.")

    def test_valid_json_but_invalid_extended_info(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10

        json_string = '{"name":"%s","capacity":\
            "%s","location": {"latitude": 55, "longitude":-30},\
            "extended_info":{"has_outlets":"true","manager":"Patty",\
            "organization":"UW"}}' % (new_name, new_capacity)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)
        self.assertEquals(response.status_code, 201,
                          "Gives a Created response to creating a Spot")
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        bad_json_string = '{"name":"%s","capacity":"%s",\
            "location": {"latitude": 55, "longitude": -30},\
            "extended_info":{"has_whiteboards":"true",\
            "has_outlets":"wub wub wub wu wu wuhhhh WUB WUB WUBBBBUB",\
            "manager":"Sam","organization":"UW"}}' % (new_name,
                                                      new_capacity)
        response = c.post('/api/v1/spot/', bad_json_string,
                          content_type="application/json", follow=False)
        self.assertEquals(response.status_code, 400,
                          "Doesn't add spot info; invalid extended info")
        self.assertEquals(Spot.objects.count(), 2,
                          "Doesn't POST spots with invalid extended info")

    def test_valid_json_but_no_extended_info(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_cap = 10

        json_string = '{"name":"%s","capacity":"%s", \
            "location": {"latitude": 55, "longitude":-30}}' % (new_name,
                                                               new_cap)
        response = c.post('/api/v1/spot/', json_string,
                          content_type="application/json", follow=False)

        error_message = json.loads(response.content)['error']
        self.assertEquals(error_message,
                          "[u'UWSpot must have extended info']",
                          "Doesn't add spot info; invalid extended info")
