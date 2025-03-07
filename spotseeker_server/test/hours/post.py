# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.test.client import Client
import simplejson as json
from django.test.utils import override_settings


@override_settings(
    SPOTSEEKER_OAUTH_ENABLED=False,
    SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms.spot."
    "DefaultSpotForm",
)
@override_settings(SPOTSEEKER_AUTH_ADMINS=("demo_user",))
class SpotHoursPOSTTest(TestCase):
    def test_hours(self):
        post_obj = {
            "name": "This spot has available hours",
            "capacity": 4,
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
        response = client.post(
            "/api/v1/spot/",
            json.dumps(post_obj),
            content_type="application/json",
        )
        get_response = client.get(response["Location"])

        self.assertEquals(
            get_response.status_code,
            200,
            "OK in response to GETing the new spot",
        )

        spot_dict = json.loads(get_response.content)

        self.maxDiff = None
        self.assertEquals(
            spot_dict["available_hours"],
            post_obj["available_hours"],
            "Data from the web service matches the data for the spot",
        )
        self.assertEquals(
            spot_dict["name"],
            post_obj["name"],
            "Data from the web service matches the data for the spot",
        )
        self.assertEquals(
            spot_dict["capacity"],
            post_obj["capacity"],
            "Data from the web service matches the data for the spot",
        )
