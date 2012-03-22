from django.utils import unittest
from django.test.client import Client
from spotseeker_server.models import Spot

class SpotDELETETest(unittest.TestCase):
    def setUp(self):
        spot = Spot.objects.create( name = "This is for testing DELETE" )
        spot.save()
        self.spot = spot

        url = '/api/v1/spot/{0}'.format(self.spot.pk)
        self.url = url

    def test_bad_url(self):
        c = Client()
        response = c.delete("/api/v1/spot/aa")
        self.assertEquals(response.status_code, 404, "Rejects an invalid url")

    def test_invalid_id_too_high(self):
        c = Client()
        test_id = self.spot.pk + 10000
        test_url = '/api/v1/spot/{0}'.format(test_id)
        response = c.delete(test_url)
        self.assertEquals(response.status_code, 404, "Rejects a not-yet existant url")

    def test_actual_delete(self):
        c = Client()
        response = c.delete(self.url)

        self.assertEquals(response.status_code, 410, "Gives a GONE in response to a valid delete")

        response = c.get(self.url)
        self.assertEquals(response.status_code, 404, "Gives a 404 on GET after a delete")

        response = c.delete(self.url)
        self.assertEquals(response.status_code, 404, "Gives a 404 on DELETE after a delete")

        test_spot = Spot.objects.get(pk=self.spot.pk)

        self.assertIsNone(test_spot, "Can't objects.get a deleted spot")



