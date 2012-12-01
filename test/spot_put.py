from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot
import simplejson as json
import random


class SpotPUTTest(TestCase):
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
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm'):
            c = Client()
            response = c.put(self.url, 'this is just text', content_type="application/json", If_Match=self.spot.etag)
            self.assertEquals(response.status_code, 400, "Rejects non-json")

    def test_invalid_url(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm'):
            c = Client()
            response = c.put("/api/v1/spot/aa", '{}', content_type="application/json")
            self.assertEquals(response.status_code, 404, "Rejects a non-numeric url")

    def test_invalid_id_too_high(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm'):
            c = Client()
            test_id = self.spot.pk + 10000
            test_url = '/api/v1/spot/{0}'.format(test_id)
            response = c.put(test_url, '{}', content_type="application/json")
            self.assertEquals(response.status_code, 404, "Rejects an id that doesn't exist yet (no PUT to create)")

    def test_empty_json(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm'):
            c = Client()
            response = c.put(self.url, '{}', content_type="application/json", If_Match=self.spot.etag)
            self.assertEquals(response.status_code, 400, "Rejects an empty body")

    def test_valid_json_no_etag(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm'):
            c = Client()
            new_name = "testing PUT name: {0}".format(random.random())
            new_capacity = 10
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30} }' % (new_name, new_capacity), content_type="application/json")
            self.assertEquals(response.status_code, 409, "Conflict w/o an etag")

            updated_spot = Spot.objects.get(pk=self.spot.pk)
            self.assertEquals(updated_spot.name, self.spot.name, "No etag - same name")
            self.assertEquals(updated_spot.capacity, self.spot.capacity, "no etag - same capacity")

    def test_valid_json_valid_etag(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm'):
            c = Client()
            new_name = "testing PUT name: {0}".format(random.random())
            new_capacity = 20

            response = c.get(self.url)
            etag = response["ETag"]

            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)
            self.assertEquals(response.status_code, 200, "Accepts a valid json string")

            updated_spot = Spot.objects.get(pk=self.spot.pk)
            self.assertEquals(updated_spot.name, new_name, "a valid PUT changes the name")
            self.assertEquals(updated_spot.capacity, new_capacity, "a valid PUT changes the capacity")

    def test_valid_json_outdated_etag(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm'):
            c = Client()
            new_name = "testing PUT name: {0}".format(random.random())
            new_capacity = 30

            response = c.get(self.url)
            etag = response["ETag"]

            intermediate_spot = Spot.objects.get(pk=self.spot.pk)
            intermediate_spot.name = "This interferes w/ the PUT"
            intermediate_spot.save()

            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)
            self.assertEquals(response.status_code, 409, "An outdated etag leads to a conflict")

            updated_spot = Spot.objects.get(pk=self.spot.pk)
            self.assertEquals(updated_spot.name, intermediate_spot.name, "keeps the intermediate name w/ an outdated etag")
            self.assertEquals(updated_spot.capacity, intermediate_spot.capacity, "keeps the intermediate capacity w/ an outdate etag")

    def test_no_duplicate_extended_info(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm'):
            c = Client()
            new_name = "testing PUT name: {0}".format(random.random())
            new_capacity = 30

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30}, "extended_info": {"has_a_funky_beat": "true"} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30}, "extended_info": {"has_a_funky_beat": "true"} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="has_a_funky_beat")), 1, 'Only has 1 has_a_funky_beat SpotExtendedInfo object after 2 PUTs')

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30}, "extended_info": {"has_a_funky_beat": "of_course"} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="has_a_funky_beat")), 1, 'Only has 1 has_a_funky_beat SpotExtendedInfo object after 3 PUTs')
            self.assertEquals(self.spot.spotextendedinfo_set.get(key="has_a_funky_beat").value, 'of_course', 'SpotExtendedInfo was updated to the latest value on put.')

    def test_deleted_spot_info(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm'):
            c = Client()
            new_name = "testing PUT name: {0}".format(random.random())
            new_capacity = 30

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30}, "extended_info": {"eats_corn_pops": "true", "rages_hard": "true", "a": "true", "b": "true", "c": "true", "d": "true"} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="eats_corn_pops")), 1, 'Has 1 eats_corn_pops SpotExtendedInfo object after 1 PUT')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="rages_hard")), 1, 'Has 1 rages_hard SpotExtendedInfo object after 1 PUT')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="a")), 1, 'Has 1 a SpotExtendedInfo object after 1 PUT')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="b")), 1, 'Has 1 b SpotExtendedInfo object after 1 PUT')

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30}, "extended_info": {"eats_corn_pops": "true"} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="eats_corn_pops")), 1, 'Has 1 eats_corn_pops SpotExtendedInfo object after a PUT')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="rages_hard")), 0, 'Has 0 rages_hard SpotExtendedInfo object after a PUT and a DELETE')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="a")), 0, 'Has 0 a SpotExtendedInfo object after 1 PUT')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="b")), 0, 'Has 0 b SpotExtendedInfo object after 1 PUT')

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="eats_corn_pops")), 0, 'Has 0 eats_corn_pops SpotExtendedInfo object after a PUT and a DELETE')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="rages_hard")), 0, 'Has 0 rages_hard SpotExtendedInfo object after a PUT and a DELETE')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="a")), 0, 'Has 0 a SpotExtendedInfo object after 1 PUT')
            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="b")), 0, 'Has 0 b SpotExtendedInfo object after 1 PUT')

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            self.assertEquals(len(self.spot.spotextendedinfo_set.filter(key="eats_corn_pops")), 0, 'Has 0 eats_corn_pops SpotExtendedInfo object after a PUT and a DELETE')

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "manager":"Yoda", "location": {"latitude": 55, "longitude": 30, "building_name": "Coruscant"} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            self.assertEquals(len(Spot.objects.get(name=new_name).manager), 4, 'Has 1 manager object after a PUT')
            self.assertEquals(len(Spot.objects.get(name=new_name).building_name), 9, 'Has 1 building_name object after a PUT')

            response = c.get(self.url)
            etag = response["ETag"]
            response = c.put(self.url, '{"name":"%s","capacity":"%d", "location": {"latitude": 55, "longitude": 30} }' % (new_name, new_capacity), content_type="application/json", If_Match=etag)

            self.assertEquals(len(Spot.objects.get(name=new_name).manager), 0, 'Has 0 manager objects after a PUT and a DELETE')
            self.assertEquals(len(Spot.objects.get(name=new_name).building_name), 0, 'Has 0 building_name objects after a PUT and a delete')
