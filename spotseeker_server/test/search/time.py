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
from django.test.client import Client
from django.test.utils import override_settings
from spotseeker_server.models import Spot, SpotAvailableHours
from spotseeker_server.cache import memory_cache


def new_spot(name):
    return Spot.objects.create(name=name)


def new_hours(spot, day, start, end):
    return SpotAvailableHours.objects.create(
        spot=spot, day=day, start_time=start, end_time=end)


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
class SpotSearchTimeTest(TestCase):

    def tearDown(self):
        memory_cache.clear_cache()

    def test_SameDayTimeInSerial(self):
        """Simple open hours test with a single date range per spot"""

        spot = new_spot('This spot is to test time ranges in search')

        spot2 = new_spot(
            'This is a second spot to test time ranges in search')

        new_hours(spot, 'f', '11:00:00', '16:00:00')
        new_hours(spot2, 'f', '11:00:00', '16:00:00')

        c = Client()

        response = c.get('/api/v1/spot/',
                         {'open_at': "Friday,11:00",
                          'open_until': "Friday,14:00"},
                         content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, spot.name)

        response = c.get('/api/v1/spot/',
                         {'open_at': "Thursday,11:00",
                          'open_until': "Thursday,15:00"},
                         content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "[]")

    def test_DiffDayTimeInSerial(self):
        """
        Each spot in this test has a small break in the middle of
        the week, so none of them show up in a query for spots open
        from 10AM mon to 10AM fri
        """

        spot = new_spot("This spot is to test time ranges in search")

        spot2 = new_spot("This is a second spot to test time ranges "
                         "in search")

        spot3 = new_spot("This is a third spot to test time "
                         "ranges in search")

        # Spot 1 hours
        new_hours(spot, 'm', '00:00:00', '13:00:00')
        new_hours(spot, 'm', '14:00:00', '23:59:59')

        for day in ('t', 'w', 'th', 'f', 'sa', 'su'):
            new_hours(spot, day, '00:00:00', '23:59:59')

        # Spot 2 hours
        new_hours(spot2, 'f', '00:00:00', '08:00:00')
        new_hours(spot2, 'f', '09:00:00', '23:59:59')

        for day in ('m', 't', 'w', 'th', 'sa', 'su'):
            new_hours(spot2, day, '00:00:00', '23:59:59')

        # Spot 3 hours
        new_hours(spot3, 'th', '00:00:00', '13:00:00')
        new_hours(spot3, 'th', '14:00:00', '23:59:59')

        for day in ('m', 't', 'w', 'f', 'sa', 'su'):
            new_hours(spot3, day, '00:00:00', '23:59:59')

        c = Client()

        response = c.get('/api/v1/spot/',
                         {'open_at': "Monday,10:00",
                          'open_until': "Friday,10:00"},
                         content_type='application/json')

        self.assertEquals(response.status_code, 200)

        # None of the spots should show up since they each have a break
        for sp in (spot, spot2, spot3):
            self.assertNotContains(response, sp.name)

    def test_SameDayTimeInReverse(self):
        """Test a date range that wraps around the end of the week"""

        spot = new_spot('This spot is to test time ranges in search')
        spot2 = new_spot(
            'This is a second spot to test time ranges in search')
        spot3 = new_spot('Third spot, same purpose')
        spot4 = new_spot('Fourth spot, same purpose')

        # Spot 1 hours, contiguous the whole week
        for day in ('m', 't', 'w', 'th', 'f', 'sa', 'su'):
            new_hours(spot, day, '00:00:00', '23:59:59')

        # Spot 2 hours
        new_hours(spot2, 'm', '11:00:00', '14:00:00')

        # Spot 3 hours
        new_hours(spot3, 'w', '08:00:00', '17:00:00')

        # Spot 4 hours, contiguous except for a block of time on monday
        new_hours(spot4, 'm', '00:00:00', '11:00:00')
        new_hours(spot4, 'm', '14:00:00', '23:59:59')

        for day in ('t', 'w', 'th', 'f', 'sa', 'su'):
            new_hours(spot4, day, '00:00:00', '23:59:59')

        c = Client()

        response = c.get('/api/v1/spot/',
                         {'open_at': "Monday,15:00",
                          'open_until': "Monday,10:00"},
                         content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, spot.name)
        self.assertNotContains(response, spot2.name)
        self.assertNotContains(response, spot3.name)
        self.assertContains(response, spot4.name)

    def test_FullWeek(self):
        """Test a spot that is open 24/7"""

        spot = new_spot('This spot is to test time ranges in search')
        spot2 = new_spot(
            'This is a second spot to test time ranges in search')

        for day in ('m', 't', 'w', 'th', 'f', 'sa', 'su'):
            new_hours(spot, day, '00:00:00', '23:59:59')

        new_hours(spot2, 'f', '08:00:00', '17:00:00')

        c = Client()

        response = c.get('/api/v1/spot/',
                         {'open_at': "Thursday,11:00",
                          'open_until': "Wednesday,20:00"},
                         content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, spot.name)
        self.assertNotContains(response, spot2.name)
