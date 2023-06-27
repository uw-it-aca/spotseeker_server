# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.test.client import Client
from spotseeker_server.models import Spot
import simplejson as json
from django.test.utils import override_settings
from django.test.utils import override_settings


@override_settings(
    SPOTSEEKER_OAUTH_ENABLED=False,
    SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms.spot."
    "DefaultSpotForm",
)
@override_settings(SPOTSEEKER_AUTH_ADMINS=("demo_user",))
class SpotHoursPUTTest(TestCase):
    def test_hours(self):
        spot = Spot.objects.create(name="This spot has available hours")
        etag = spot.etag

        put_obj = {
            "name": "This spot has available hours",
            "capacity": "4",
            "location": {
                "latitude": "55",
                "longitude": "30",
            },
            "available_hours": {
                "monday": [["00:00", "10:00"], ["11:00", "14:00"]],
                "tuesday": [["11:00", "14:00"]],
                "wednesday": [["11:00", "14:00"]],
                "thursday": [["11:00", "14:00"]],
                "friday": [["11:00", "14:00"]],
                "saturday": [],
                "sunday": [["11:00", "14:00"]],
            },
        }

        client = Client()
        url = "/api/v1/spot/%s" % spot.pk
        response = client.put(
            url,
            json.dumps(put_obj),
            content_type="application/json",
            If_Match=etag,
        )
        spot_dict = json.loads(response.content)

        self.maxDiff = None
        self.assertEquals(
            spot_dict["available_hours"],
            put_obj["available_hours"],
            "Data from the web service matches the data for the spot",
        )
