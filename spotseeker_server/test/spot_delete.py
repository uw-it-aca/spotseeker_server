# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.test.client import Client
from spotseeker_server.models import Spot
from django.test.utils import override_settings


@override_settings(
    SPOTSEEKER_OAUTH_ENABLED=False,
    SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms.spot."
    "DefaultSpotForm",
)
@override_settings(SPOTSEEKER_AUTH_ADMINS=("demo_user",))
class SpotDELETETest(TestCase):
    """Tests deleting a Spot."""

    def setUp(self):
        spot = Spot.objects.create(name="This is for testing DELETE")
        spot.save()
        self.spot = spot

        url = "/api/v1/spot/{0}".format(self.spot.pk)
        self.url = url

    def test_bad_url(self):
        c = Client()
        response = c.delete("/api/v1/spot/aa")
        self.assertEqual(response.status_code, 404)

    def test_invalid_id_too_high(self):
        c = Client()
        test_id = self.spot.pk + 10000
        test_url = "/api/v1/spot/{0}".format(test_id)
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
