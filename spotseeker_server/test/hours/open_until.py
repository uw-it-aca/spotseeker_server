# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.test.utils import override_settings
from django.test.client import Client
import mock
from spotseeker_server.models import Spot, SpotAvailableHours
import simplejson as json
from datetime import datetime, timedelta
import datetime as alternate_date
import time
from mock import patch
from spotseeker_server import models


@override_settings(SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok")
class SpotHoursOpenUntilTest(TestCase):
    """Tests search requests for spots that are open at a particular time."""

    @mock.patch("spotseeker_server.views.search.SearchView.get_datetime")
    def test_open_until(self, datetime_mock):
        # Create a spot that isn't open now but will be in an hour.
        spot = Spot.objects.create(name="This spot is open later")
        # Setting now to be Wednesday 9:00:00
        now = datetime(16, 2, 3, 9, 0, 0).time()

        spot_open = alternate_date.time(now.hour + 1, now.minute)
        spot_close = alternate_date.time(now.hour + 3, now.minute)

        day_lookup = ["su", "m", "t", "w", "th", "f", "sa"]
        today = day_lookup[3]

        SpotAvailableHours.objects.create(
            spot=spot, day=today, start_time=spot_open, end_time=spot_close
        )

        # Mock the call to now() so that the time returned
        # is always 9:00:00
        datetime_mock.return_value = ("w", datetime(16, 2, 3, 9, 0, 0).time())

        # Verify the spot is closed now
        client = Client()
        response = client.get("/api/v1/spot", {"open_now": True})
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s["id"] == spot.pk:
                spot_returned = True

        self.assertTrue(
            not spot_returned,
            "The spot that is open later is not in the " "spots open now",
        )

        # Get a spot that is open until spot_close
        at_time = alternate_date.time(now.hour + 2, now.minute)
        at_time = at_time.strftime("%H:%M")
        until_time = spot_close.strftime("%H:%M")
        day_dict = {
            "su": "Sunday",
            "m": "Monday",
            "t": "Tuesday",
            "w": "Wednesday",
            "th": "Thursday",
            "f": "Friday",
            "sa": "Saturday",
        }
        at_query_day = day_dict[today]
        at_query = "%s,%s" % (at_query_day, at_time)
        until_query = "%s,%s" % (at_query_day, until_time)

        response = client.get(
            "/api/v1/spot", {"open_at": at_query, "open_until": until_query}
        )
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s["id"] == spot.pk:
                spot_returned = True

        self.assertTrue(spot_returned, "Got the spot that is open later")

    def test_open_window_ok(self):
        spot = Spot.objects.create(name="Spot with window")

        SpotAvailableHours.objects.create(
            spot=spot, day="m", start_time="09:30:00", end_time="13:30:00"
        )

        client = Client()
        response = client.get(
            "/api/v1/spot",
            {"open_at": "Monday,09:30", "open_until": "Monday,13:30"},
        )
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s["id"] == spot.pk:
                spot_returned = True

        self.assertTrue(spot_returned, "Got the spot with the full window")

    def test_open_window_with_gap(self):
        spot = Spot.objects.create(name="Spot with window gap")

        SpotAvailableHours.objects.create(
            spot=spot, day="m", start_time="09:30:00", end_time="10:30:00"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="m", start_time="11:30:00", end_time="13:30:00"
        )

        client = Client()
        response = client.get(
            "/api/v1/spot",
            {"open_at": "Monday,09:30", "open_until": "Monday,13:30"},
        )
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s["id"] == spot.pk:
                spot_returned = True

        self.assertFalse(spot_returned, "Didn't find the spot with the gap")

    def test_open_window_multiple_days(self):
        spot = Spot.objects.create(name="Spot with window - multiple days")

        SpotAvailableHours.objects.create(
            spot=spot, day="m", start_time="09:30:00", end_time="23:59:59"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="t", start_time="00:00:00", end_time="14:00:00"
        )

        client = Client()
        response = client.get(
            "/api/v1/spot",
            {"open_at": "Monday,09:30", "open_until": "Tuesday,13:30"},
        )
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s["id"] == spot.pk:
                spot_returned = True

        self.assertTrue(spot_returned, "Found the spot w/ an overnight window")

    def test_open_window_multiple_days_gap(self):
        spot = Spot.objects.create(name="Spot with window - multiple days")

        SpotAvailableHours.objects.create(
            spot=spot, day="m", start_time="09:30:00", end_time="22:59:59"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="t", start_time="00:00:00", end_time="14:00:00"
        )

        client = Client()
        response = client.get(
            "/api/v1/spot",
            {"open_at": "Monday,09:30", "open_until": "Tuesday,13:30"},
        )
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s["id"] == spot.pk:
                spot_returned = True

        self.assertFalse(
            spot_returned,
            "Didn't find the spot w/ an overnight window, " "with a gap in it",
        )

    def test_open_window_multiple_days_long(self):
        spot = Spot.objects.create(name="Spot with window - multiple days")

        SpotAvailableHours.objects.create(
            spot=spot, day="m", start_time="09:30:00", end_time="23:59:59"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="t", start_time="00:00:00", end_time="23:59:59"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="w", start_time="00:00:00", end_time="23:59:59"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="th", start_time="00:00:00", end_time="14:00:00"
        )

        client = Client()
        response = client.get(
            "/api/v1/spot",
            {"open_at": "Monday,09:30", "open_until": "Thursday,13:30"},
        )
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s["id"] == spot.pk:
                spot_returned = True

        self.assertTrue(spot_returned, "Found the spot w/ a longer window")

    def test_open_window_multiple_days_gap_long(self):
        spot = Spot.objects.create(name="Spot with window - multiple days")

        SpotAvailableHours.objects.create(
            spot=spot, day="m", start_time="09:30:00", end_time="23:59:59"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="t", start_time="00:00:00", end_time="14:00:00"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="t", start_time="16:00:00", end_time="23:59:59"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="w", start_time="00:00:00", end_time="23:59:59"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="th", start_time="00:00:00", end_time="14:00:00"
        )

        client = Client()
        response = client.get(
            "/api/v1/spot",
            {"open_at": "Monday,09:30", "open_until": "Thursday,13:30"},
        )
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s["id"] == spot.pk:
                spot_returned = True

        self.assertFalse(
            spot_returned,
            "Didn't find the spot w/ a longer window, " "with a gap in it",
        )

    def test_open_window_around_weekend(self):
        spot = Spot.objects.create(name="Spot with window - multiple days")

        SpotAvailableHours.objects.create(
            spot=spot, day="f", start_time="09:30:00", end_time="23:59:59"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="sa", start_time="00:00:00", end_time="23:59:59"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="su", start_time="00:00:00", end_time="23:59:59"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="m", start_time="00:00:00", end_time="14:00:00"
        )

        client = Client()
        response = client.get(
            "/api/v1/spot",
            {"open_at": "Friday,09:30", "open_until": "Monday,13:30"},
        )
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s["id"] == spot.pk:
                spot_returned = True

        self.assertTrue(spot_returned, "Found the spot open over the weekend")

    def test_open_window_around_weekend_gap(self):
        spot = Spot.objects.create(name="Spot with window - multiple days")

        SpotAvailableHours.objects.create(
            spot=spot, day="f", start_time="09:30:00", end_time="23:59:59"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="sa", start_time="00:00:00", end_time="14:00:00"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="sa", start_time="16:00:00", end_time="23:59:59"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="su", start_time="00:00:00", end_time="23:59:59"
        )
        SpotAvailableHours.objects.create(
            spot=spot, day="m", start_time="00:00:00", end_time="14:00:00"
        )

        client = Client()
        response = client.get(
            "/api/v1/spot",
            {"open_at": "Friday,09:30", "open_until": "Monday,13:30"},
        )
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s["id"] == spot.pk:
                spot_returned = True

        self.assertFalse(
            spot_returned, "Didn't find the spot w/ a gap over the weekend"
        )
