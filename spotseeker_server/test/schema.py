# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from spotseeker_server.models import *
from django.test.client import Client
from django.test import TestCase
import simplejson as json
from mock import patch
from spotseeker_server import models
from django.test.utils import override_settings


@override_settings(SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok")
@override_settings(
    SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms.spot."
    "DefaultSpotForm"
)
@override_settings(
    SPOTSEEKER_SPOTEXTENDEDINFO_FORM="spotseeker_server.default_forms.spot."
    "DefaultSpotExtendedInfoForm"
)
class SpotSchemaTest(TestCase):
    def test_content_type(self):
        c = Client()
        url = "/api/v1/schema"
        response = c.get(url)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_regular_spot_info(self):
        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)

        self.assertEqual(schema["manager"], "unicode")
        self.assertEqual(schema["capacity"], "int")
        self.assertEqual(schema["last_modified"], "auto")
        self.assertEqual(schema["uri"], "auto")

    def test_location_spot_info(self):
        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        schema_location = schema["location"]

        self.assertEqual(schema_location["latitude"], "decimal")
        self.assertEqual(schema_location["room_number"], "unicode")
        self.assertEqual(schema_location["floor"], "unicode")

    def test_spot_image_info(self):
        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        schema_image = schema["images"][0]

        self.assertEqual(schema_image["description"], "unicode")
        self.assertEqual(schema_image["modification_date"], "auto")
        self.assertEqual(schema_image["width"], "int")

    def test_spot_types(self):
        SpotType.objects.create(name="Jedi")
        SpotType.objects.create(name="Sith")

        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        schema_types = schema["type"]

        self.assertEqual(len(schema_types), 2)
        SpotType.objects.create(name="Ewok")

        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        schema_types = schema["type"]

        self.assertEqual(len(schema_types), 3)

    def test_extended_info(self):
        test_spot = Spot.objects.create(id=1, name="Test")

        SpotExtendedInfo.objects.create(
            spot=test_spot,
            key="noise_level",
            value=["silent", "quiet", "moderate", "loud", "variable"],
        )
        SpotExtendedInfo.objects.create(
            spot=test_spot, key="has_computers", value=["true"]
        )
        SpotExtendedInfo.objects.create(
            spot=test_spot, key="orientation", value="unicode"
        )
        SpotExtendedInfo.objects.create(
            spot=test_spot, key="num_computers", value="int"
        )

        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        extended_info = schema["extended_info"]

        self.assertEqual(extended_info["noise_level"], "unicode")
        self.assertEqual(extended_info["has_computers"], "unicode")
        self.assertEqual(extended_info["orientation"], "unicode")
        self.assertEqual(extended_info["num_computers"], "unicode")
