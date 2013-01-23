from spotseeker_server.models import *
from django.test.client import Client
from django.test import TestCase
import simplejson as json


class UWSpotSchemaTest(TestCase):
    def test_extended_info(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
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
