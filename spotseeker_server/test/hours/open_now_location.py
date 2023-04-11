# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot, SpotAvailableHours
import simplejson as json
from datetime import datetime
import datetime as alternate_date
from decimal import *
import mock

from time import *
from django.test.utils import override_settings
from mock import patch
from spotseeker_server import models


@override_settings(SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok")
class SpotHoursOpenNowLocationTest(TestCase):
    """Tests that available Spots that are in location range are returned
    but available Spots outside the location range are not returned.
    """

    @mock.patch("spotseeker_server.views.search.SearchView.get_datetime")
    def test_open_now(self, datetime_mock):
        open_in_range_spot = Spot.objects.create(
            name="This spot is open now",
            latitude=Decimal("40.0000898315"),
            longitude=Decimal("-50.0"),
        )
        closed_in_range_spot = Spot.objects.create(
            name="This spot is closed now",
            latitude=Decimal("40.0000898315"),
            longitude=Decimal("-50.0"),
        )

        open_outof_range_spot = Spot.objects.create(
            name="This spot is open now",
            latitude=Decimal("45.0000898315"),
            longitude=Decimal("-55.0"),
        )
        closed_outof_range_spot = Spot.objects.create(
            name="This spot is closed now",
            latitude=Decimal("45.0000898315"),
            longitude=Decimal("-55.0"),
        )

        # Setting now to be Wednesday 9:00:00
        now = datetime(16, 2, 3, 9, 0, 0).time()

        open_start = alternate_date.time(now.hour - 1, now.minute)
        open_end = alternate_date.time(now.hour + 1, now.minute)

        closed_start = alternate_date.time(now.hour + 1, now.minute)
        closed_end = alternate_date.time(now.hour + 2, now.minute)

        day_lookup = ["su", "m", "t", "w", "th", "f", "sa"]
        today = day_lookup[3]

        open_hours1 = SpotAvailableHours.objects.create(
            spot=open_in_range_spot,
            day=today,
            start_time=open_start,
            end_time=open_end,
        )
        closed_hours1 = SpotAvailableHours.objects.create(
            spot=closed_in_range_spot,
            day=today,
            start_time=closed_start,
            end_time=closed_end,
        )

        open_hours2 = SpotAvailableHours.objects.create(
            spot=open_outof_range_spot,
            day=today,
            start_time=open_start,
            end_time=open_end,
        )
        closed_hours2 = SpotAvailableHours.objects.create(
            spot=closed_outof_range_spot,
            day=today,
            start_time=closed_start,
            end_time=closed_end,
        )
        # Mock the call to now() so that the time returned
        # is always 9:00:00
        datetime_mock.return_value = ("w", datetime(16, 2, 3, 9, 0, 0).time())
        client = Client()
        response = client.get(
            "/api/v1/spot",
            {
                "center_latitude": "40",
                "center_longitude": -50,
                "distance": 100,
                "open_now": True,
            },
        )
        spots = json.loads(response.content)

        has_open_in_range = False
        has_open_outof_range = False
        has_closed_in_range = False
        has_closed_outof_range = False

        for spot in spots:
            if spot["id"] == open_in_range_spot.pk:
                has_open_in_range = True
            if spot["id"] == closed_in_range_spot.pk:
                has_closed_in_range = True
            if spot["id"] == open_outof_range_spot.pk:
                has_open_outof_range = True
            if spot["id"] == closed_outof_range_spot.pk:
                has_closed_outof_range = True

        self.assertEquals(
            has_open_in_range, True, "Found the open spot in range"
        )
        self.assertEquals(
            has_closed_in_range, False, "Did not find the closed spot in range"
        )
        self.assertEquals(
            has_open_outof_range,
            False,
            "Did not find the open spot out of range",
        )
        self.assertEquals(
            has_closed_outof_range,
            False,
            "Did not find the closed spot out of range",
        )
