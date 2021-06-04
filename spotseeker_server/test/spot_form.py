# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from spotseeker_server.default_forms.spot import DefaultSpotForm
from spotseeker_server.forms.spot import SpotForm
from django.conf import settings
from django.test.utils import override_settings


@override_settings(
    SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok",
    SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms.spot."
    "DefaultSpotForm",
    SPOTSEEKER_SPOTEXTENDEDINFO_FORM="spotseeker_server.default_forms.spot."
    "DefaultSpotExtendedInfoForm",
)
class DefaultSpotFormTest(TestCase):
    def test_default(self):
        form = SpotForm({})
        self.assertIs(
            type(form),
            DefaultSpotForm,
            "Tests shouldn't be run with a defined " "SPOTSEEKER_SPOT_FORM",
        )

    def test_errors(self):
        """Assert that an empty form produces validation errors"""
        form = SpotForm({})
        errors = form.errors
        self.assertIn("name", errors)
        # Capacity is not required, so it should not have an error
        self.assertNotIn("capacity", errors)
