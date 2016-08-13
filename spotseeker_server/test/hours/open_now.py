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
from spotseeker_server.models import Spot, SpotAvailableHours
import simplejson as json
from datetime import datetime
import datetime as alternate_date
import mock

from time import *
from django.test.utils import override_settings
from mock import patch
from spotseeker_server import models
from spotseeker_server.cache import memory_cache


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
class SpotHoursOpenNowTest(TestCase):
    """ Tests that we can tell if a Spot is available now,
    based on it's Available Hours.
    """
    def setUp(self):
        memory_cache.clear_cache()

    @mock.patch('spotseeker_server.views.search.SearchView.get_datetime')
    def test_open_now(self, datetime_mock):
        open_spot = Spot.objects.create(name="This spot is open now")
        no_hours_spot = Spot.objects.create(name="This spot has no hours")
        closed_spot = Spot.objects.create(
            name="This spot has hours, but is closed")

        # Setting now to be Wednesday 9:00:00
        now = datetime(16, 2, 3, 9, 0, 0).time()

        open_start = alternate_date.time(now.hour - 1, now.minute)
        open_end = alternate_date.time(now.hour + 1, now.minute)

        closed_start = alternate_date.time(now.hour + 1, now.minute)
        closed_end = alternate_date.time(now.hour + 2, now.minute)

        day_lookup = ["su", "m", "t", "w", "th", "f", "sa"]
        today = day_lookup[3]

        open_hours = SpotAvailableHours.objects.create(
            spot=open_spot,
            day=today,
            start_time=open_start,
            end_time=open_end)
        closed_hours = SpotAvailableHours.objects.create(
            spot=closed_spot,
            day=today,
            start_time=closed_start,
            end_time=closed_end)

        # Mock the call to now() so that the time returned
        # is always 9:00:00
        datetime_mock.return_value = ('w',
                                      datetime(16, 2, 3, 9, 0, 0).time())

        # Testing to make sure too small of a radius returns nothing
        client = Client()
        response = client.get("/api/v1/spot", {'open_now': True})
        self.assertEquals(response.status_code, 200)
        spots = json.loads(response.content)

        has_open_spot = False
        has_closed_spot = False
        has_no_hours_spot = False

        for spot in spots:
            if spot['id'] == open_spot.pk:
                has_open_spot = True

            if spot['id'] == closed_spot.pk:
                has_closed_spot = True

            if spot['id'] == no_hours_spot.pk:
                has_no_hours_spot = True

        self.assertEquals(has_closed_spot,
                          False,
                          "Doesn't find the closed spot")
        self.assertEquals(has_no_hours_spot,
                          False,
                          "Doesn't find the spot with no hours")
        self.assertEquals(has_open_spot, True, "Finds the open spot")

    @mock.patch('spotseeker_server.views.search.SearchView.get_datetime')
    def test_thirty_sec_before_midnight(self, datetime_mock):
        """ Tests when the user makes a request between 23:59 and 00:00.
        """
        open_spot = Spot.objects.create(name="Spot open overnight")
        open_hours = SpotAvailableHours.objects.create(
            spot=open_spot,
            day='m',
            start_time=datetime(12, 03, 12, 18, 00, 00).time(),
            end_time=datetime(12, 03, 12, 23, 59, 00).time())
        open_hours = SpotAvailableHours.objects.create(
            spot=open_spot,
            day='t',
            start_time=datetime(12, 03, 12, 00, 00, 00).time(),
            end_time=datetime(12, 03, 12, 06, 00, 00).time())
        early_open_spot = Spot.objects.create(name="Spot open at midnight")
        open_hours = SpotAvailableHours.objects.create(
            spot=early_open_spot,
            day='t',
            start_time=datetime(12, 03, 12, 00, 00, 00).time(),
            end_time=datetime(12, 03, 12, 18, 00, 00).time())

        # Mock the call to now() so that the time returned
        # is 23:59:30
        datetime_mock.return_value = (
            'm',
            datetime(12, 03, 12, 23, 59, 30).time())

        c = Client()
        response = c.get("/api/v1/spot", {'open_now': True})
        self.assertEqual(response.status_code, 200)

        spots = json.loads(response.content)
        self.assertTrue(open_spot.json_data_structure() in spots)
        # confirm spots openning at midnight are not returned
        self.assertTrue(early_open_spot.json_data_structure() not in spots)

        # mock the call to now() so that the time reutrned
        # is 23:59:00
        datetime_mock.return_value = (
            'm',
            datetime(12, 03, 12, 23, 59, 00).time())
        response = c.get("/api/v1/spot", {'open_now': True})
        self.assertEqual(response.status_code, 200)

        spots = json.loads(response.content)
        self.assertTrue(open_spot.json_data_structure() in spots)
        # confirm spots openning at midnight are not returned
        self.assertTrue(early_open_spot.json_data_structure() not in spots)

        # mock the call to now() so that the time reutrned
        # is 23:58:30
        datetime_mock.return_value = (
            'm',
            datetime(12, 03, 12, 23, 58, 30).time())
        response = c.get("/api/v1/spot", {'open_now': True})
        self.assertEqual(response.status_code, 200)

        spots = json.loads(response.content)
        self.assertTrue(open_spot.json_data_structure() in spots)
        # confirm spots openning at midnight are not returned
        self.assertTrue(early_open_spot.json_data_structure() not in spots)

        # mock the call to now() so that the time reutrned
        # is 23:58:00
        datetime_mock.return_value = (
            'm',
            datetime(12, 03, 12, 23, 58, 00).time())
        response = c.get("/api/v1/spot", {'open_now': True})
        self.assertEqual(response.status_code, 200)

        spots = json.loads(response.content)
        self.assertTrue(open_spot.json_data_structure() in spots)
        # confirm spots openning at midnight are not returned
        self.assertTrue(early_open_spot.json_data_structure() not in spots)
