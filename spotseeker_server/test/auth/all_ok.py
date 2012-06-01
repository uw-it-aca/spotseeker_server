from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot, SpotExtendedInfo
import simplejson as json


class SpotAuthAllOK(TestCase):
    """ Tests that the all_ok auth module successfully allows any client access.
    """
    settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok'

    def setUp(self):
        spot = Spot.objects.create(name="This is for testing the all ok auth module", capacity=10)
        extended = SpotExtendedInfo.objects.create(spot=spot, key="whiteboards", value=True)
        self.spot = spot
        self.url = "/api/v1/spot/%s" % self.spot.pk

    def test_get(self):
        c = Client()
        response = c.get(self.url)
        spot_dict = json.loads(response.content)
        returned_spot = Spot.objects.get(pk=spot_dict['id'])
        self.assertEquals(returned_spot, self.spot, "Returns the correct spot")

    def test_put(self):
        c = Client()

        response = c.get(self.url)
        etag = response["ETag"]

        spot_dict = json.loads(response.content)
        spot_dict['name'] = "Modifying all ok"

        # Tests the org specific SPOT_FORM if it's set in settings.py
        response = c.put(self.url, json.dumps(spot_dict), content_type="application/json", If_Match=etag)
        self.assertEquals(response.status_code, 200, "Accepts a valid json string")

        # Additionally test with the default spot form if there's an org specific one
        if settings.SPOTSEEKER_SPOT_FORM:
            with self.settings(SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm'):
                # The previous PUT in the test changed the ETag!
                response = c.get(self.url)
                etag = response['ETag']
                response = c.put(self.url, json.dumps(spot_dict), content_type="application/json", If_Match=etag)
                self.assertEquals(response.status_code, 200, "Accepts a valid json string")

        updated_spot = Spot.objects.get(pk=self.spot.pk)
        self.assertEquals(updated_spot.name, "Modifying all ok", "a valid PUT changes the name")
