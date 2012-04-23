from django.utils import unittest
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot
import simplejson as json
import random

class SpotPOSTTest(unittest.TestCase):
    settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok';
    def test_valid_json(self):
        c = Client()
        new_name = "testing POST name: {0}".format(random.random())
        new_capacity = 10
        response = c.post('/api/v1/spot/', '{{"name":"{0}","capacity":"{1}"}}'.format(new_name, new_capacity), content_type="application/json", follow=False)

        self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

        # XXX - I'm not sure if anything below here is valid
        self.assertIn("Location", response, "The response has a location header")

        # Assuming tests are sequential - make a spot, and the spot before it should be the POST
        next_spot = Spot.objects.create(name = "This is just to get the id")
        next_spot.save()

        next_pk = next_spot.pk

        post_pk = next_pk - 1

        self.assertEquals(response["Location"], "http://testserver/api/v1/spot/{0}".format(post_pk), "The uri for the new spot is correct")

        get_response = c.get(response["Location"])
        self.assertEquals(get_response.status_code, 200, "OK in response to GETing the new spot")

        spot_json = json.loads(get_response.content)

        self.assertEquals(spot_json["name"], new_name, "The right name was stored")
        self.assertEquals(spot_json["capacity"], new_capacity, "The right capacity was stored")

    def test_non_json(self):
        c = Client()
        response = c.post('/api/v1/spot/', 'just a string', content_type="application/json", follow=False)
        self.assertEquals(response.status_code, 400)

    def test_invalid_json(self):
        c = Client()
        response = c.post('/api/v1/spot/', '{}', content_type="application/json", follow=False)
        self.assertEquals(response.status_code, 400)


