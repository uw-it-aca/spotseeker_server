from django.utils import unittest
from django.test.client import Client
from spotseeker_server.models import Spot

class SpotGETTest(unittest.TestCase):
    def setUp(self):
        spot = Spot.objects.create( name = "This is for testing GET" )
        spot.save()
        self.spot = spot

    def test_invalid_id_too_high(self):
        c = Client()
        last_spot = list(Spot.objects.all())[-1]
        url = "/api/v1/spot/%s" % (last_spot.pk + 1)
        response = c.get(url)
        self.assertEquals(response.status_code, 404, "Spot ID too high")
