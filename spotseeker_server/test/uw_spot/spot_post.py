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
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_whiteboards":"true","has_outlets":"false","manager":"Bob","organization":"UW"}}' % (new_name, new_capacity)
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

    def test_uw_field_has_whiteboards(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            whiteboards = 12
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_whiteboards":"%s","has_outlets":"true","manager":"John","organization":"UW"}}' % (new_name, new_capacity, whiteboards)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because has_whiteboards field did not pass validation")

            whiteboards = 'false'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_whiteboards":"%s","has_outlets":"true","manager":"John","organization":"UW"}}' % (new_name, new_capacity, whiteboards)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_has_outlets(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            outlets = 12

            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_whiteboards":"false","manager":"Harry","organization":"UW"}}' % (new_name, new_capacity)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)
            self.assertEquals(response.status_code, 400, "Not created because has_outlets was not included")

            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_whiteboards":"false","has_outlets":"%s","manager":"Harry","organization":"UW"}}' % (new_name, new_capacity, outlets)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)
            self.assertEquals(response.status_code, 400, "Not created because has_outlets field did not pass validation")

            outlets = 'true'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_whiteboards":"false","has_outlets":"%s","manager":"Harry","organization":"UW"}}' % (new_name, new_capacity, outlets)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)
            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_has_printing(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            printer = 12
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","has_printing":"%s","manager":"Gary","organization":"UW"}}' % (new_name, new_capacity, printer)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because has_printing field did not pass validation")

            printer = 'true'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","has_printing":"%s","manager":"Gary","organization":"UW"}}' % (new_name, new_capacity, printer)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_has_scanner(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            scanner = 'There are none'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","has_scanner":"%s","manager":"Sally","organization":"UW"}}' % (new_name, new_capacity, scanner)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because has_scanner field did not pass validation")

            scanner = 'true'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","has_scanner":"%s","manager":"Sally","organization":"UW"}}' % (new_name, new_capacity, scanner)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_has_displays(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            has_displays = 'There are none'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","has_displays":"%s","manager":"Fred","organization":"UW"}}' % (new_name, new_capacity, has_displays)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because has_displays field did not pass validation")

            has_displays = 'false'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","has_displays":"%s","manager":"Fred","organization":"UW"}}' % (new_name, new_capacity, has_displays)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_has_projector(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            has_projector = 'There are none'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","has_projector":"%s","manager":"George","organization":"UW"}}' % (new_name, new_capacity, has_projector)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because has_projector field did not pass validation")

            has_projector = 'false'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","has_projector":"%s","manager":"George","organization":"UW"}}' % (new_name, new_capacity, has_projector)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_computers(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            computers = 'There are none'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","has_computers":"%s","manager":"Tina","organization":"UW"}}' % (new_name, new_capacity, computers)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because computers field did not pass validation")

            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","has_computers":"true","manager":"Tina","organization":"UW"}}' % (new_name, new_capacity)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_has_natural_light(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            has_natural_light = 'Nope!'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","has_natural_light":"%s","manager":"Mary","organization":"UW"}}' % (new_name, new_capacity, has_natural_light)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because has_natural_light field did not pass validation")

            has_natural_light = 'true'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","has_natural_light":"%s","manager":"Mary","organization":"UW"}}' % (new_name, new_capacity, has_natural_light)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_noise_level(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            noise_level = 'Rock Concert'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","noise_level":"%s","manager":"Patty","organization":"UW"}}' % (new_name, new_capacity, noise_level)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because noise_level field did not pass validation")

            noise_level = 'moderate'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","noise_level":"%s","manager":"Patty","organization":"UW"}}' % (new_name, new_capacity, noise_level)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_food_nearby(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            food_nearby = 'In the area'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","food_nearby":"%s","manager":"Kristy","organization":"UW"}}' % (new_name, new_capacity, food_nearby)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because food_nearby field did not pass validation")

            food_nearby = 'building'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","food_nearby":"%s","manager":"Kristy","organization":"UW"}}' % (new_name, new_capacity, food_nearby)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_reservable(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10
            reservable = 'You bet'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","reservable":"%s","manager":"Patty","organization":"UW"}}' % (new_name, new_capacity, reservable)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 400, "Not created because reservable field did not pass validation")

            reservable = 'reservations'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","reservable":"%s","manager":"Patty","organization":"UW"}}' % (new_name, new_capacity, reservable)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

    def test_uw_field_reservable(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing POST name: {0}".format(random.random())
            new_capacity = 10

            desc = 'This is a description'
            json_string = '{"name":"%s","capacity":"%s","extended_info":{"has_outlets":"true","description":"%s","manager":"Patty","organization":"UW"}}' % (new_name, new_capacity, desc)
            response = c.post('/api/v1/spot/', json_string, content_type="application/json", follow=False)

            self.assertEquals(response.status_code, 201, "Gives a Created response to creating a Spot")

            spot = Spot.objects.get(name=new_name)
            spot_desc = spot.spotextendedinfo_set.get(key='description').value

            self.assertEquals(desc, spot_desc, "The Spot's description matches what was POSTed.")
