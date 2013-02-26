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
from django.test.utils import override_settings
from django.test.client import Client
from django.utils.unittest import skipIf
from spotseeker_server.models import Spot, SpotAvailableHours
import simplejson as json
from datetime import datetime, timedelta
import time


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
class SpotHoursOpenUntilTest(TestCase):
    """ Tests search requests for spots that are open at a particular time.
    """

    @skipIf(datetime.now().hour + 3 > 23 or datetime.now().hour < 3, "Skip open_at tests due to the time of day")
    def test_open_until(self):
        # Create a spot that isn't open now but will be in an hour.
        spot = Spot.objects.create(name="This spot is open later")
        now = datetime.now()
        spot_open = datetime.time(now + timedelta(hours=1))
        spot_close = datetime.time(now + timedelta(hours=3))

        day_lookup = ["su", "m", "t", "w", "th", "f", "sa"]
        day_num = int(time.strftime("%w", time.localtime()))
        today = day_lookup[day_num]

        SpotAvailableHours.objects.create(spot=spot, day=today, start_time=spot_open, end_time=spot_close)

        # Verify the spot is closed now
        c = Client()
        response = c.get("/api/v1/spot", {'open_now': True})
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s['id'] == spot.pk:
                spot_returned = True

        self.assertTrue(not spot_returned, "The spot that is open later is not in the spots open now")

        # Get a spot that is open until spot_close
        at_time = datetime.time(now + timedelta(hours=2))
        at_time = at_time.strftime("%H:%M")
        until_time = spot_close.strftime("%H:%M")
        day_dict = {"su": "Sunday",
                    "m": "Monday",
                    "t": "Tuesday",
                    "w": "Wednesday",
                    "th": "Thursday",
                    "f": "Friday",
                    "sa": "Saturday", }
        at_query_day = day_dict[today]
        at_query = "%s,%s" % (at_query_day, at_time)
        until_query = "%s,%s" % (at_query_day, until_time)

        response = c.get("/api/v1/spot", {'open_at': at_query, 'open_until': until_query})
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s['id'] == spot.pk:
                spot_returned = True

        self.assertTrue(spot_returned, "Got the spot that is open later")

    def test_open_window_ok(self):
        spot = Spot.objects.create(name="Spot with window")

        SpotAvailableHours.objects.create(spot=spot, day="m", start_time="09:30:00", end_time="13:30:00")

        c = Client()
        response = c.get("/api/v1/spot", {'open_at': "Monday,09:30", 'open_until': "Monday,13:30"})
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s['id'] == spot.pk:
                spot_returned = True

        self.assertTrue(spot_returned, "Got the spot with the full window")

    def test_open_window_with_gap(self):
        spot = Spot.objects.create(name="Spot with window gap")

        SpotAvailableHours.objects.create(spot=spot, day="m", start_time="09:30:00", end_time="10:30:00")
        SpotAvailableHours.objects.create(spot=spot, day="m", start_time="11:30:00", end_time="13:30:00")

        c = Client()
        response = c.get("/api/v1/spot", {'open_at': "Monday,09:30", 'open_until': "Monday,13:30"})
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s['id'] == spot.pk:
                spot_returned = True

        self.assertFalse(spot_returned, "Didn't find the spot with the gap")

    def test_open_window_multiple_days(self):
        spot = Spot.objects.create(name="Spot with window - multiple days")

        SpotAvailableHours.objects.create(spot=spot, day="m", start_time="09:30:00", end_time="23:59:59")
        SpotAvailableHours.objects.create(spot=spot, day="t", start_time="00:00:00", end_time="14:00:00")

        c = Client()
        response = c.get("/api/v1/spot", {'open_at': "Monday,09:30", 'open_until': "Tuesday,13:30"})
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s['id'] == spot.pk:
                spot_returned = True

        self.assertTrue(spot_returned, "Found the spot w/ an overnight window")

    def test_open_window_multiple_days_gap(self):
        spot = Spot.objects.create(name="Spot with window - multiple days")

        SpotAvailableHours.objects.create(spot=spot, day="m", start_time="09:30:00", end_time="22:59:59")
        SpotAvailableHours.objects.create(spot=spot, day="t", start_time="00:00:00", end_time="14:00:00")

        c = Client()
        response = c.get("/api/v1/spot", {'open_at': "Monday,09:30", 'open_until': "Tuesday,13:30"})
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s['id'] == spot.pk:
                spot_returned = True

        self.assertFalse(spot_returned, "Didn't find the spot w/ an overnight window, with a gap in it")

    def test_open_window_multiple_days_long(self):
        spot = Spot.objects.create(name="Spot with window - multiple days")

        SpotAvailableHours.objects.create(spot=spot, day="m", start_time="09:30:00", end_time="23:59:59")
        SpotAvailableHours.objects.create(spot=spot, day="t", start_time="00:00:00", end_time="23:59:59")
        SpotAvailableHours.objects.create(spot=spot, day="w", start_time="00:00:00", end_time="23:59:59")
        SpotAvailableHours.objects.create(spot=spot, day="th", start_time="00:00:00", end_time="14:00:00")

        c = Client()
        response = c.get("/api/v1/spot", {'open_at': "Monday,09:30", 'open_until': "Thursday,13:30"})
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s['id'] == spot.pk:
                spot_returned = True

        self.assertTrue(spot_returned, "Found the spot w/ a longer window")

    def test_open_window_multiple_days_gap_long(self):
        spot = Spot.objects.create(name="Spot with window - multiple days")

        SpotAvailableHours.objects.create(spot=spot, day="m", start_time="09:30:00", end_time="23:59:59")
        SpotAvailableHours.objects.create(spot=spot, day="t", start_time="00:00:00", end_time="14:00:00")
        SpotAvailableHours.objects.create(spot=spot, day="t", start_time="16:00:00", end_time="23:59:59")
        SpotAvailableHours.objects.create(spot=spot, day="w", start_time="00:00:00", end_time="23:59:59")
        SpotAvailableHours.objects.create(spot=spot, day="th", start_time="00:00:00", end_time="14:00:00")

        c = Client()
        response = c.get("/api/v1/spot", {'open_at': "Monday,09:30", 'open_until': "Thursday,13:30"})
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s['id'] == spot.pk:
                spot_returned = True

        self.assertFalse(spot_returned, "Didn't find the spot w/ a longer window, with a gap in it")

    def test_open_window_around_weekend(self):
        spot = Spot.objects.create(name="Spot with window - multiple days")

        SpotAvailableHours.objects.create(spot=spot, day="f", start_time="09:30:00", end_time="23:59:59")
        SpotAvailableHours.objects.create(spot=spot, day="sa", start_time="00:00:00", end_time="23:59:59")
        SpotAvailableHours.objects.create(spot=spot, day="su", start_time="00:00:00", end_time="23:59:59")
        SpotAvailableHours.objects.create(spot=spot, day="m", start_time="00:00:00", end_time="14:00:00")

        c = Client()
        response = c.get("/api/v1/spot", {'open_at': "Friday,09:30", 'open_until': "Monday,13:30"})
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s['id'] == spot.pk:
                spot_returned = True

        self.assertTrue(spot_returned, "Found the spot open over the weekend")

    def test_open_window_around_weekend_gap(self):
        spot = Spot.objects.create(name="Spot with window - multiple days")

        SpotAvailableHours.objects.create(spot=spot, day="f", start_time="09:30:00", end_time="23:59:59")
        SpotAvailableHours.objects.create(spot=spot, day="sa", start_time="00:00:00", end_time="14:00:00")
        SpotAvailableHours.objects.create(spot=spot, day="sa", start_time="16:00:00", end_time="23:59:59")
        SpotAvailableHours.objects.create(spot=spot, day="su", start_time="00:00:00", end_time="23:59:59")
        SpotAvailableHours.objects.create(spot=spot, day="m", start_time="00:00:00", end_time="14:00:00")

        c = Client()
        response = c.get("/api/v1/spot", {'open_at': "Friday,09:30", 'open_until': "Monday,13:30"})
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s['id'] == spot.pk:
                spot_returned = True

        self.assertFalse(spot_returned, "Didn't find the spot w/ a gap over the weekend")
