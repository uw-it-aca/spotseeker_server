# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from spotseeker_server.org_forms.uw_spot import UWSpotForm
from spotseeker_server.org_forms.uw_spot import UWSpotExtendedInfoForm
from django.conf import settings
from django.test.utils import override_settings

ALL_OK = "spotseeker_server.auth.all_ok"
UW_SPOT_FORM = "spotseeker_server.org_forms.uw_spot.UWSpotForm"
UW_EXT_INFO_FORM = "spotseeker_server.org_forms.uw.spot.UWSpotExtendedInfoForm"


@override_settings(SPOTSEEKER_AUTH_MODULE=ALL_OK)
@override_settings(SPOTSEEKER_SPOT_FORM=UW_SPOT_FORM)
@override_settings(SPOTSEEKER_SPOTEXTENDEDINFO_FORM=UW_EXT_INFO_FORM)
class UWSpotFormTest(TestCase):
    def test_spot_form_errors(self):
        form = UWSpotForm({})
        errors = form.errors
        self.assertTrue("name" in errors, "UW spot form requires a name")
        self.assertTrue("latitude" in errors, "UW spot form requires latitude")
        self.assertTrue(
            "longitude" in errors, "UW spot form requires longitude"
        )

    def test_spotextendedinfo_form_errors(self):
        form = UWSpotForm(
            {"name": "fo' testing dawg", "latitude": "45", "longitude": "-125"}
        )
        self.assertEquals({}, form.errors, "UW SpotForm error.")
        spot = form.save()

        a_form = UWSpotExtendedInfoForm(
            {"spot": spot.id, "key": "noise_level", "value": "quiet"}
        )
        b_form = UWSpotExtendedInfoForm(
            {"spot": spot.id, "key": "has_computers", "value": "true"}
        )
        c_form = UWSpotExtendedInfoForm(
            {"spot": spot.id, "key": "orientation", "value": "North"}
        )
        d_form = UWSpotExtendedInfoForm(
            {"spot": spot.id, "key": "num_computers", "value": 15}
        )

        a_errors = a_form.errors
        b_errors = b_form.errors
        c_errors = c_form.errors
        d_errors = d_form.errors

        self.assertEquals(
            {}, a_errors, "UW SpotExtendedInfo noise_level error."
        )
        self.assertEquals(
            {}, b_errors, "UW SpotExtendedInfo has_computers error."
        )
        self.assertEquals(
            {}, c_errors, "UW SpotExtendedInfo orientation error."
        )
        self.assertEquals(
            {}, d_errors, "UW SpotExtendedInfo num_computers error."
        )
