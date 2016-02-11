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

from spotseeker_server.models import *
from django.test.client import Client
from django.test import TestCase
import simplejson as json
from mock import patch
from django.core import cache
from spotseeker_server import models
from django.test.utils import override_settings


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
@override_settings(SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm')
@override_settings(SPOTSEEKER_SPOTEXTENDEDINFO_FORM='spotseeker_server.default_forms.spot.DefaultSpotExtendedInfoForm')
class SpotSchemaTest(TestCase):
    def test_content_type(self):
        c = Client()
        url = "/api/v1/schema"
        response = c.get(url)
        self.assertEquals(response["Content-Type"], "application/json", "Has the json header")

    def test_regular_spot_info(self):
        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)

        self.assertEquals(schema["manager"], "unicode", "Schema Regular Spot Info matches the actual Regular Spot Info")
        self.assertEquals(schema["capacity"], "int", "Schema Regular Spot Info matches the actual Regular Spot Info")
        self.assertEquals(schema["last_modified"], "auto", "Schema Regular Spot Info matches the actual Regular Spot Info")
        self.assertEquals(schema["uri"], "auto", "Schema Regular Spot Info matches the actual Regular Spot Info")

    def test_location_spot_info(self):
        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        schema_location = schema["location"]

        self.assertEquals(schema_location["latitude"], "decimal", "Schema Location Spot Info matches the actual Location Spot Info")
        self.assertEquals(schema_location["room_number"], "unicode", "Schema Location Spot Info matches the actual Location Spot Info")
        self.assertEquals(schema_location["floor"], "unicode", "Schema Location Spot Info matches the actual Location Spot Info")

    def test_spot_image_info(self):
        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        schema_image = schema["images"][0]

        self.assertEquals(schema_image["description"], "unicode", "Schema Spot Image Info matches the actual Spot Image Info")
        self.assertEquals(schema_image["modification_date"], "auto", "Schema Spot Image Info matches the actual Spot Image Info")
        self.assertEquals(schema_image["width"], "int", "Schema Spot Image Info matches the actual Spot Image Info")

    def test_spot_types(self):
        SpotType.objects.create(name="Jedi")
        SpotType.objects.create(name="Sith")

        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        schema_types = schema["type"]

        self.assertEquals(len(schema_types), 2, "Schema SpotType matches the actual SpotType")
        SpotType.objects.create(name="Ewok")

        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        schema_types = schema["type"]

        self.assertEquals(len(schema_types), 3, "Schema SpotType matches the actual SpotType")

    def test_extended_info(self):
        test_spot = Spot.objects.create(id=1, name="Test")

        SpotExtendedInfo.objects.create(spot=test_spot, key="noise_level", value=["silent", "quiet", "moderate", "loud", "variable"])
        SpotExtendedInfo.objects.create(spot=test_spot, key="has_computers", value=["true"])
        SpotExtendedInfo.objects.create(spot=test_spot, key="orientation", value="unicode")
        SpotExtendedInfo.objects.create(spot=test_spot, key="num_computers", value="int")

        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        extended_info = schema["extended_info"]

        self.assertEquals(extended_info["noise_level"], "unicode", "Schema ExtendedInfo matches the actual ExtendedInfo")
        self.assertEquals(extended_info["has_computers"], "unicode", "Schema ExtendedInfo matches the actual ExtendedInfo")
        self.assertEquals(extended_info["orientation"], "unicode", "Schema ExtendedInfo matches the actual ExtendedInfo")
        self.assertEquals(extended_info["num_computers"], "unicode", "Schema ExtendedInfo matches the actual ExtendedInfo")
