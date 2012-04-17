from django.utils import unittest
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot
import simplejson as json

class SpotGETTest(unittest.TestCase):
    settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok';
    def setUp(self):
        spot = Spot.objects.create( name = "This is for testing GET" )
        spot.save()
        self.spot = spot

    def test_invalid_id(self):
        c = Client()
        response = c.get("/api/v1/spot/bad_id")
        self.assertEquals(response.status_code, 404, "Rejects a non-numeric id")

    def test_invalid_id_too_high(self):
        c = Client()
        url = "/api/v1/spot/%s" % (self.spot.pk + 10000)
        response = c.get(url)
        self.assertEquals(response.status_code, 404, "Spot ID too high")

    def test_content_type(self):
        c = Client()
        url = "/api/v1/spot/%s" % self.spot.pk
        response = c.get(url)
        self.assertEquals(response["Content-Type"], "application/json", "Has the json header")

    def test_etag(self):
        c = Client()
        url = "/api/v1/spot/%s" % self.spot.pk
        response = c.get(url)
        self.assertEquals(response["ETag"], self.spot.etag, "Have the correct ETag header")

    def test_invalid_params(self):
        c = Client()
        url = "/api/v1/spot/%s" % self.spot.pk
        response = c.get(url, {'bad_param':'does not exist'},)
        self.assertEquals(response.status_code, 200, "Accepts a query string")
        spot_dict = json.loads(response.content)
        returned_spot = Spot.objects.get(pk=spot_dict['id'])
        self.assertEquals(returned_spot, self.spot, "Returns the correct spot")

    def test_valid_id(self):
        c = Client()
        url = "/api/v1/spot/%s" % self.spot.pk
        response = c.get(url)
        spot_dict = json.loads(response.content)
        returned_spot = Spot.objects.get(pk=spot_dict['id'])
        self.assertEquals(response.status_code, 200, "Accepts a valid id")
        self.assertEquals(returned_spot, self.spot, "Returns the correct spot")
