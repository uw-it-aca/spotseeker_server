from django.utils import unittest
from spotseeker_server.default_forms.spot import DefaultSpotForm
from spotseeker_server.forms.spot import SpotForm
from django.conf import settings


class SpotFormTest(unittest.TestCase):
    settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok'
    settings.SPOTSEEKER_SPOT_FORM = 'spotseeker_server.default_forms.spot.DefaultSpotForm'

    def test_default(self):
        form = SpotForm({})
        self.assertEqual(form.__class__, DefaultSpotForm({}).__class__, "Tests shouldn't be run with a defined SPOTSEEKER_SPOT_FORM")

    def test_errors(self):
        form = SpotForm({})
        errors = form.errors
        self.assertTrue("name" in errors, "Default spot form requires a spot name")
        self.assertFalse("capacity" in errors, "Default spot form doesn't require a spot name")
