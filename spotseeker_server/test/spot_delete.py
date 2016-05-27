""" Copyright 2012, 2013 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot
from django.test.utils import override_settings
from mock import patch
from spotseeker_server import models


@override_settings(
    SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
    SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.'
                         'DefaultSpotForm')
@override_settings(SPOTSEEKER_AUTH_ADMINS=('demo_user',))
class SpotDELETETest(TestCase):
    """ Tests deleting a Spot.
    """

    def setUp(self):
        spot = Spot.objects.create(name="This is for testing DELETE")
        spot.save()
        self.spot = spot

        url = '/api/v1/spot/{0}'.format(self.spot.pk)
        self.url = url

    def test_bad_url(self):
        c = Client()
        response = c.delete("/api/v1/spot/aa")
        self.assertEqual(response.status_code, 404)

    def test_invalid_id_too_high(self):
        c = Client()
        test_id = self.spot.pk + 10000
        test_url = '/api/v1/spot/{0}'.format(test_id)
        response = c.delete(test_url)
        self.assertEqual(response.status_code, 404)

    def test_actual_delete_with_etag(self):
        c = Client()
        response = c.get(self.url)
        etag = response["ETag"]
        response = c.delete(self.url, If_Match=etag)

        self.assertEqual(response.status_code, 200)

        response = c.get(self.url)
        self.assertEqual(response.status_code, 404)

        response = c.delete(self.url)
        self.assertEqual(response.status_code, 404)

        try:
            test_spot = Spot.objects.get(pk=self.spot.pk)
        except Exception as e:
            test_spot = None

        self.assertIsNone(test_spot, "Can't objects.get a deleted spot")

    def test_actual_delete_no_etag(self):
        c = Client()

        response = c.delete(self.url)
        self.assertEqual(response.status_code, 400)

        response = c.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_actual_delete_expired_etag(self):
        c = Client()

        response = c.get(self.url)
        etag = response["ETag"]

        intermediate_spot = Spot.objects.get(pk=self.spot.pk)
        intermediate_spot.name = "This interferes w/ the DELETE"
        intermediate_spot.save()

        response = c.delete(self.url, If_Match=etag)
        self.assertEqual(response.status_code, 409)

        response = c.get(self.url)
        self.assertEqual(response.status_code, 200)
