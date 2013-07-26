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

from django.test import TestCase
from spotseeker_server.org_forms.uw_spot import UWSpotForm, UWSpotExtendedInfoForm
from django.conf import settings
from django.test.utils import override_settings


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
@override_settings(SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm')
@override_settings(SPOTSEEKER_SPOTEXTENDEDINFO_FORM='spotseeker_server.org_forms.uw_spot.UWSpotExtendedInfoForm')
class UWSpotFormTest(TestCase):
    def test_spot_form_errors(self):
        form = UWSpotForm({})
        errors = form.errors
        self.assertTrue("name" in errors, "UW spot form requires a name")
        self.assertTrue("latitude" in errors, "UW spot form requires latitude")
        self.assertTrue("longitude" in errors, "UW spot form requires longitude")

    def test_spotextendedinfo_form_errors(self):
        form = UWSpotForm({"name": "fo' testing dawg", "latitude": "45", "longitude": "-125"})
        self.assertEquals({}, form.errors, "UW SpotForm error.")
        spot = form.save()

        a_form = UWSpotExtendedInfoForm({"spot": spot.id, "key": "noise_level", "value": "quiet"})
        b_form = UWSpotExtendedInfoForm({"spot": spot.id, "key": "has_computers", "value": "true"})
        c_form = UWSpotExtendedInfoForm({"spot": spot.id, "key": "orientation", "value": "North"})
        d_form = UWSpotExtendedInfoForm({"spot": spot.id, "key": "num_computers", "value": 15})

        a_errors = a_form.errors
        b_errors = b_form.errors
        c_errors = c_form.errors
        d_errors = d_form.errors

        self.assertEquals({}, a_errors, "UW SpotExtendedInfo noise_level error.")
        self.assertEquals({}, b_errors, "UW SpotExtendedInfo has_computers error.")
        self.assertEquals({}, c_errors, "UW SpotExtendedInfo orientation error.")
        self.assertEquals({}, d_errors, "UW SpotExtendedInfo num_computers error.")
