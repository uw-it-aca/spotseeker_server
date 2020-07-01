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
from django.core.exceptions import ValidationError
import datetime
from spotseeker_server.models import Spot, SpotAvailableHours


class SpotHoursModelTest(TestCase):
    """ Tests for Spot AvailableHours.
    """

    def test_startMatchesEnd(self):
        """ Tests that a Spot's AvailableHours cannot have zero length.
        """
        with self.settings(
                SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok'):
            spot = Spot.objects.create(name='testing hours')
            with self.assertRaises(Exception,
                msg="Got an error trying to save a time range with no time in it",
            ) as ex:
                SpotAvailableHours.objects.create(
                    day="m", spot=spot,  start_time="01:30", end_time="01:30"
                )
            self.assertEqual(
                ex.exception.args[0],
                "Invalid time range - start time must be before end time"
            )

    def test_startAfterEnd(self):
        """ Tests that a Spot's AvailableHours cannot end before they begin.
        """
        with self.settings(
                SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok'):
            spot = Spot.objects.create(name='testing hours')
            with self.assertRaises(Exception,
                msg="Got an error trying to save a time range with no time in it",
            ) as ex:
                SpotAvailableHours.objects.create(
                    day="m", spot=spot,  start_time="01:30", end_time="01:30"
                )
            self.assertEqual(
                ex.exception.args[0],
                "Invalid time range - start time must be before end time"
            )

    def test_properRange(self):
        """ Tests that having AvailableHours with a start time before the
            end time saves properly.
        """
        with self.settings(
                SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok'):
            spot = Spot.objects.create(name='testing hours')
            hours = SpotAvailableHours.objects.create(day="m",
                                                      spot=spot,
                                                      start_time="01:30",
                                                      end_time="01:40")

            self.assertEqual(hours.start_time, datetime.time(1, 30), "ok")
            self.assertEqual(hours.end_time, datetime.time(1, 40), "ok")
            self.assertEqual(hours.day, "m", "ok")

    def test_missingStart(self):
        """ Tests that AvailableHours cannot be created with no start time.
        """
        with self.settings(
                SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok'):
            spot = Spot.objects.create(name='testing hours')
            has_error = False
            try:
                hours = SpotAvailableHours.objects.create(spot=spot,
                                                          day="m",
                                                          end_time="01:30")
            except ValidationError:
                has_error = True

            self.assertEqual(has_error,
                             True,
                             "Doesn't allow hours to be stored without a "
                             "start time")

    def test_missingEnd(self):
        """ Tests that AvailableHours cannot be created with no end time.
        """
        with self.settings(
                SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok'):
            spot = Spot.objects.create(name='testing hours')
            has_error = False
            try:
                hours = SpotAvailableHours.objects.create(spot=spot,
                                                          day="m",
                                                          start_time="01:30")
            except ValidationError:
                has_error = True

            self.assertEqual(has_error,
                             True,
                             "Doesn't allow hours to be stored without "
                             "an end time")

    def test_missingHours(self):
        """ Tests that AvailableHourse cannot be created with out a time range.
        """
        with self.settings(
                SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok'):
            spot = Spot.objects.create(name='testing hours')
            has_error = False
            try:
                hours = SpotAvailableHours.objects.create(spot=spot, day="m")
            except ValidationError:
                has_error = True

            self.assertEqual(has_error,
                             True,
                             "Doesn't allow hours to be stored without hours")

    def test_missingDay(self):
        """ Tests that AvailableHours cannot be \
            created without a day of the week.
        """
        with self.settings(
                SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok'):
            spot = Spot.objects.create(name='testing hours')
            has_error = False
            try:
                hours = SpotAvailableHours.objects.create(spot=spot,
                                                          start_time="01:30",
                                                          end_time="02:30")
            except ValidationError:
                has_error = True

            self.assertEqual(has_error,
                             True,
                             "Doesn't allow hours to be stored without a day")

    def test_invalidDay(self):
        """ Tests that AvailableHours cannot be created with a day that
            doesn't exist as a day of the week.
        """
        with self.settings(
                SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok'):
            spot = Spot.objects.create(name='testing hours')
            has_error = False
            try:
                hours = SpotAvailableHours.objects.create(spot=spot,
                                                          day="Fail_day",
                                                          start_time="01:30",
                                                          end_time="02:30")
            except Exception as e:
                has_error = True

            self.assertEqual(has_error,
                             True,
                             "Doesn't allow hours to be stored "
                             "with an invalid day")
