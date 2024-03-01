# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.conf import settings
from spotseeker_server.models import Spot
import simplejson as json
from django.test.utils import override_settings


@override_settings(SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok")
class SpotAuthAllOK(TestCase):
    """Tests that the all_ok auth module
    successfully allows any client access.
    """

    def setUp(self):
        spot = Spot.objects.create(
            name="This is for testing the all ok auth module", capacity=10
        )
        self.spot = spot
        self.url = "/api/v1/spot/%s" % self.spot.pk

    def test_get(self):
        c = self.client
        response = c.get(self.url)
        spot_dict = json.loads(response.content)
        returned_spot = Spot.objects.get(pk=spot_dict["id"])
        self.assertEquals(returned_spot, self.spot, "Returns the correct spot")

    @override_settings(
        SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms."
        "spot.DefaultSpotForm",
        SPOTSEEKER_SPOTEXTENDEDINFO_FORM="spotseeker_server.default_forms."
        "spot.DefaultSpotExtendedInfoForm",
        SPOTSEEKER_AUTH_ADMINS=("demo_user",),
    )
    def test_put(self):
        c = self.client
        response = c.get(self.url)
        etag = response["ETag"]

        spot_dict = json.loads(response.content)
        spot_dict["location"] = {"latitude": 55, "longitude": -30}
        spot_dict["name"] = "Modifying all ok"

        response = c.put(
            self.url,
            json.dumps(spot_dict),
            content_type="application/json",
            If_Match=etag,
        )
        self.assertEquals(
            response.status_code, 200, "Accepts a valid json string"
        )

        updated_spot = Spot.objects.get(pk=self.spot.pk)
        self.assertEquals(
            updated_spot.name,
            "Modifying all ok",
            "a valid PUT changes the name",
        )
