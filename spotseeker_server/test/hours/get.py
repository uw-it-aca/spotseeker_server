# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot, SpotAvailableHours
import simplejson as json
from django.test.utils import override_settings
from mock import patch
from spotseeker_server import models


@override_settings(SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok")
class SpotHoursGETTest(TestCase):
    def setUp(self):
        spot = Spot.objects.create(name="This spot has available hours")
        # Intentionally out of order - make sure windows are sorted, not
        # just in db happenstance order
        hours2 = SpotAvailableHours.objects.create(
            spot=spot, day="m", start_time="11:00", end_time="14:00"
        )
        hours1 = SpotAvailableHours.objects.create(
            spot=spot, day="m", start_time="00:00", end_time="10:00"
        )
        hours3 = SpotAvailableHours.objects.create(
            spot=spot, day="t", start_time="11:00", end_time="14:00"
        )
        hours4 = SpotAvailableHours.objects.create(
            spot=spot, day="w", start_time="11:00", end_time="14:00"
        )
        hours5 = SpotAvailableHours.objects.create(
            spot=spot, day="th", start_time="11:00", end_time="14:00"
        )
        hours6 = SpotAvailableHours.objects.create(
            spot=spot, day="f", start_time="11:00", end_time="14:00"
        )
        # Saturday is intentionally missing
        hours8 = SpotAvailableHours.objects.create(
            spot=spot, day="su", start_time="11:00", end_time="14:00"
        )

        self.spot = spot

    def test_hours(self):
        """Tests that a Spot's available hours can be retrieved successfully.
        """
        c = Client()
        url = "/api/v1/spot/%s" % self.spot.pk
        response = c.get(url)
        spot_dict = json.loads(response.content)

        valid_data = {
            "monday": [["00:00", "10:00"], ["11:00", "14:00"]],
            "tuesday": [["11:00", "14:00"]],
            "wednesday": [["11:00", "14:00"]],
            "thursday": [["11:00", "14:00"]],
            "friday": [["11:00", "14:00"]],
            "saturday": [],
            "sunday": [["11:00", "14:00"]],
        }

        available_hours = spot_dict["available_hours"]
        self.assertEqual(available_hours, valid_data)
