from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot
import simplejson as json


class SpotAuthAllOK(TestCase):
    """ Tests that the all_ok auth module successfully allows any client access.
    """

    def setUp(self):
        spot = Spot.objects.create(name="This is for testing the all ok auth module", capacity=10)
        self.spot = spot
        self.url = "/api/v1/spot/%s" % self.spot.pk

    def test_get(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok'):
            c = Client()
            response = c.get(self.url)
            spot_dict = json.loads(response.content)
            returned_spot = Spot.objects.get(pk=spot_dict['id'])
            self.assertEquals(returned_spot, self.spot, "Returns the correct spot")

    def test_put(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm'):
            c = Client()

            response = c.get(self.url)
            etag = response["ETag"]

            spot_dict = json.loads(response.content)
            spot_dict["location"] = {"latitude": 55, "longitude": -30}
            spot_dict['name'] = "Modifying all ok"

            response = c.put(self.url, json.dumps(spot_dict), content_type="application/json", If_Match=etag)
            self.assertEquals(response.status_code, 200, "Accepts a valid json string")

            updated_spot = Spot.objects.get(pk=self.spot.pk)
            self.assertEquals(updated_spot.name, "Modifying all ok", "a valid PUT changes the name")
