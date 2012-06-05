from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot
import simplejson as json
import random


class UWSpotPOSTTest(TestCase):
    """ Tests creating a new Spot via POST.
    """

    def test_valid_json(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"whiteboards":"True","outlets":"False"}}' % (new_name, new_capacity)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

            # XXX - I'm not sure if anything below here is valid
            self.assertIn("Location", response, "The response has a location header")

            # Assuming tests are sequential - make a spot, and the spot before it should be the POST
            next_spot = Spot.objects.create(name="This is just to get the id")
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
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            response = c.post('/api/v1/spot/', 'just a string', content_type="application/json", follow=False)
            self.assertEquals(response.status_code, 400)

    def test_invalid_json(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            response = c.post('/api/v1/spot/', '{}', content_type="application/json", follow=False)
            self.assertEquals(response.status_code, 400)

    def test_uw_field_whiteboards(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            whiteboards = 12
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"whiteboards":"%s","outlets":"True"}}' % (new_name, new_capacity, whiteboards)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because whiteboards field did not pass validation")

            whiteboards = 'False'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"whiteboards":"%s","outlets":"True"}}' % (new_name, new_capacity, whiteboards)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_outlets(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            outlets = 12

            json_string = '{"name":"%s","capacity":"%s","extended_info":{"whiteboards":"False"}}' % (new_name, new_capacity)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)
            self.assertEquals(response.status_code, 400, "Not created because outlets was not included")

            json_string = '{"name":"%s","capacity":"%s","extended_info":{"whiteboards":"False","outlets":"%s"}}' % (new_name, new_capacity, outlets)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)
            self.assertEquals(response.status_code, 400, "Not created because outlets field did not pass validation")

            outlets = 'True'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"whiteboards":"False","outlets":"%s"}}' % (new_name, new_capacity, outlets)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)
            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_printer(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            printer = 12
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"outlets":"True","printer":"%s"}}' % (new_name, new_capacity, printer)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because printer field did not pass validation")

            printer = 'In building'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"outlets":"True","printer":"%s"}}' % (new_name, new_capacity, printer)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")
