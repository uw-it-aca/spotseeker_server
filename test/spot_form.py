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
from spotseeker_server.default_forms.spot import DefaultSpotForm
from django.conf import settings
from mock import patch
from spotseeker_server.default_forms.spot import DefaultSpotForm as default_spot
import spotseeker_server.auth.all_ok as ss_all_ok

@patch('spotseeker_server.forms.spot.SpotForm', default_spot)
@patch('spotseeker_server.require_auth.APP_AUTH_METHOD', ss_all_ok.authenticate_application)
@patch('spotseeker_server.require_auth.USER_AUTH_METHOD', ss_all_ok.authenticate_user)
class SpotFormTest(TestCase):
    """
    this class doesn't import SpotForm at the top and instead allows the methods
    to import SpotForm themselves.  This way, we can patch the SpotForm object for
    the duration of the test to use the DefaultSpotForm instead of whatever is
    defined in local_settings
    """

    def test_default(self):
        from spotseeker_server.forms.spot import SpotForm
        form = SpotForm({})
        self.assertEqual(form.__class__, DefaultSpotForm({}).__class__, "Tests shouldn't be run with a defined SPOTSEEKER_SPOT_FORM")

    def test_errors(self):
        from spotseeker_server.forms.spot import SpotForm
        form = SpotForm({})
        errors = form.errors
        self.assertTrue("name" in errors, "Default spot form requires a spot name")
        self.assertFalse("capacity" in errors, "Default spot form doesn't require a spot name")
