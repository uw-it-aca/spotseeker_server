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

from django.test.utils import override_settings
from spotseeker_server.models import *
from django.test.client import Client
from django.test import TestCase
import simplejson as json


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
@override_settings(SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm')
@override_settings(SPOTSEEKER_SPOTEXTENDEDINFO_FORM='spotseeker_server.org_forms.uw_spot.UWSpotExtendedInfoForm')
class UWSpotSchemaTest(TestCase):
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

        self.assertEquals(extended_info["noise_level"], ["silent", "quiet", "moderate", "loud", "variable"], "Schema ExtendedInfo matches the actual ExtendedInfo")
        self.assertEquals(extended_info["has_computers"], ["true"], "Schema ExtendedInfo matches the actual ExtendedInfo")
        self.assertEquals(extended_info["orientation"], "unicode", "Schema ExtendedInfo matches the actual ExtendedInfo")
        self.assertEquals(extended_info["num_computers"], "int", "Schema ExtendedInfo matches the actual ExtendedInfo")
