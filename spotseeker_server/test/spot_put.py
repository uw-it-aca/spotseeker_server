from django.utils import unittest
from django.test.client import Client
from spotseeker_server.models import Spot
from django.db import transaction
import random

class SpotPUTTest(unittest.TestCase):
    def setUp(self):
        spot = Spot.objects.create( name = "This is for testing PUT" )
        spot.save()
        self.spot = spot

        url = '/api/v1/spot/{0}'.format(self.spot.pk)
        self.url = url

    def test_bad_json(self):
        c = Client()
        response = c.put(self.url, 'this is just text', content_type="application/json")
        print response

    def test_invalid_url(self):
        c = Client()
        response = c.put("/api/v1/spot/aa", '{}', content_type="application/json")
        self.assertEquals(response.status_code, 404, "Rejects a non-numeric url")
        print response

    def test_invalid_id_too_high(self):
        c = Client()
        test_id = self.spot.pk + 10000
        test_url = '/api/v1/spot/{0}'.format(test_id)
        response = c.put(test_url, '{}', content_type="application/json")
        self.assertEquals(response.status_code, 404, "Rejects an id that doesn't exist yet (no PUT to create)")
        print response

    def test_empty_json(self):
        c = Client()
        response = c.put(self.url, '{}', content_type="application/json")
        self.assertEquals(response.status_code, 400, "Rejects an empty body")

    def test_valid_json(self):
        c = Client()
        new_name = "testing PUT name: {0}".format(random.random())
        new_capacity = "testing PUT capacity: {0}".format(random.random())
        response = c.put(self.url, '{{"name":"{0}","capacity":"{1}"}}'.format(new_name, new_capacity), content_type="application/json")
        print "Response: ", response
        self.assertEquals(response.status_code, 200, "Accepts a valid json string")

        updated_spot = Spot.objects.get(pk=self.spot.pk)
        self.assertEquals(updated_spot.name, new_name, "a valid PUT changes the name")
        self.assertEquals(updated_spot.capacity, new_capacity, "a valid PUT changes the capacity")

