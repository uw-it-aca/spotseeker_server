from django.utils import unittest
from spotseeker_server.forms.spot import SpotForm
from django.conf import settings


class UWSpotFormTest(unittest.TestCase):
    settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok'
    settings.SPOTSEEKER_SPOT_FORM = 'spotseeker_server.org_forms.uw_spot.UWSpotForm'

    def test_errors(self):
        form = SpotForm({})
        errors = form.errors
        self.assertTrue("extended_info" in errors, "UW spot form requires extended_info")
