# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test.utils import override_settings
from spotseeker_server.models import *
from django.test.client import Client
from django.test import TestCase
import simplejson as json


ALL_OK = "spotseeker_server.auth.all_ok"
UW_SPOT_FORM = "spotseeker_server.org_forms.uw_spot.UWSpotForm"
UW_EXT_INFO_FORM = "spotseeker_server.org_forms.uw_spot.UWSpotExtendedInfoForm"


@override_settings(SPOTSEEKER_AUTH_MODULE=ALL_OK)
@override_settings(SPOTSEEKER_SPOT_FORM=UW_SPOT_FORM)
@override_settings(SPOTSEEKER_SPOTEXTENDEDINFO_FORM=UW_EXT_INFO_FORM)
class UWSpotSchemaTest(TestCase):
    def test_extended_info(self):
        test_spot = Spot.objects.create(id=1, name="Test")

        SpotExtendedInfo.objects.create(
            spot=test_spot,
            key="noise_level",
            value=["silent", "quiet", "moderate", "variable"],
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

        self.assertEquals(
            extended_info["noise_level"],
            ["silent", "quiet", "moderate", "variable"],
            "Schema ExtendedInfo matches actual ExtendedInfo",
        )
        self.assertEquals(
            extended_info["has_computers"],
            ["true"],
            "Schema ExtendedInfo matches actual ExtendedInfo",
        )
        self.assertEquals(
            extended_info["orientation"],
            "unicode",
            "Schema ExtendedInfo matches actual ExtendedInfo",
        )
        self.assertEquals(
            extended_info["num_computers"],
            "int",
            "Schema ExtendedInfo matches actual ExtendedInfo",
        )
