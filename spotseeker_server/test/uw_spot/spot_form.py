from django.test import TestCase
from spotseeker_server.forms.spot import SpotForm
from django.conf import settings


class UWSpotFormTest(TestCase):

    def test_errors(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            form = SpotForm({})
            errors = form.errors
            self.assertTrue("extended_info" in errors, "UW spot form requires extended_info")
