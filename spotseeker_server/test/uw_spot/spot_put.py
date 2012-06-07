from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot
import random


class UWSpotPUTTest(TestCase):
    """ Tests updating Spot information via PUT.
    """

    def setUp(self):
        spot = Spot.objects.create(name="This is for testing PUT")
        spot.save()
        self.spot = spot

        url = '/api/v1/spot/{0}'.format(self.spot.pk)
        self.url = url

    def test_bad_json(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            response = c.put(self.url, 'this is just text', content_type="application/json", If_Match=self.spot.etag)
            self.assertEquals(response.status_code, 400, "Rejects non-json")

    def test_invalid_url(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            response = c.put("/api/v1/spot/aa", '{}', content_type="application/json")
            self.assertEquals(response.status_code, 404, "Rejects a non-numeric url")

    def test_invalid_id_too_high(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            test_id = self.spot.pk + 10000
            test_url = '/api/v1/spot/{0}'.format(test_id)
            response = c.put(test_url, '{}', content_type="application/json")
            self.assertEquals(response.status_code, 404, "Rejects an id that doesn't exist yet (no PUT to create)")

    def test_empty_json(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            response = c.put(self.url, '{}', content_type="application/json", If_Match=self.spot.etag)
            self.assertEquals(response.status_code, 400, "Rejects an empty body")

    def test_valid_json_no_etag(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing PUT name: {0}".format(random.random())
            new_capacity = 10
            response = c.put(self.url, '{{"name":"{0}","capacity":"{1}"}}'.format(new_name, new_capacity), content_type="application/json")
            self.assertEquals(response.status_code, 409, "Conflict w/o an etag")

            updated_spot = Spot.objects.get(pk=self.spot.pk)
            self.assertEquals(updated_spot.name, self.spot.name, "No etag - same name")
            self.assertEquals(updated_spot.capacity, self.spot.capacity, "no etag - same capacity")

    def test_valid_json_valid_etag(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing PUT name: {0}".format(random.random())
            new_capacity = 20

            response = c.get(self.url)
            etag = response["ETag"]

            json_string = '{"name":"%s","capacity":"%s","extended_info":{"whiteboards":"1","has_outlets":"1","manager":"Sam","organization":"UW"}}' % (new_name, new_capacity)
            response = c.put(self.url, json_string, content_type="application/json", If_Match=etag)
            self.assertEquals(response.status_code, 200, "Accepts a valid json string")

            updated_spot = Spot.objects.get(pk=self.spot.pk)
            self.assertEquals(updated_spot.name, new_name, "a valid PUT changes the name")
            self.assertEquals(updated_spot.capacity, new_capacity, "a valid PUT changes the capacity")

    def test_valid_json_outdated_etag(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.org_forms.uw_spot.UWSpotForm'):
            c = Client()
            new_name = "testing PUT name: {0}".format(random.random())
            new_capacity = 30

            response = c.get(self.url)
            etag = response["ETag"]

            intermediate_spot = Spot.objects.get(pk=self.spot.pk)
            intermediate_spot.name = "This interferes w/ the PUT"
            intermediate_spot.save()

            response = c.put(self.url, '{{"name":"{0}","capacity":"{1}"}}'.format(new_name, new_capacity), content_type="application/json", If_Match=etag)
            self.assertEquals(response.status_code, 409, "An outdated etag leads to a conflict")

            updated_spot = Spot.objects.get(pk=self.spot.pk)
            self.assertEquals(updated_spot.name, intermediate_spot.name, "keeps the intermediate name w/ an outdated etag")
            self.assertEquals(updated_spot.capacity, intermediate_spot.capacity, "keeps the intermediate capacity w/ an outdate etag")
