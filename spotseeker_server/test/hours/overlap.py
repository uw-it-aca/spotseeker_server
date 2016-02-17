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

from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from spotseeker_server.models import Spot, SpotAvailableHours


class SpotHoursOverlapTest(TestCase):
    """ Tests that when open hours are submitted that overlap with other open hours for a Spot, the previous Spot hours are adjusted rather than having multiple AvailableHours hanging around.
    """
    def setUp(self):
        spot = Spot.objects.create(name="This spot has overlapping hours")
        self.spot = spot

    def test_early_overlap(self):
        """ Tests adding SpotAvailableHours with a start time earlier than an existing start, but end within the current open hours.
        """
        hours1 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="09:00", end_time="12:00")
        hours2 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="07:00", end_time="10:00")

        # creating hours2 should get those times merged into hours1
        hours_obj_count = self.spot.spotavailablehours_set.values_list().count()
        self.assertEquals(hours_obj_count, 1, "Only one SpotAvailableHours object")

        # check to see that start and end times are correct
        new_hours = self.spot.spotavailablehours_set.all()[0]
        self.assertEquals(hours2.start_time, new_hours.start_time, "Start time is the same")
        self.assertEquals(hours1.end_time, new_hours.end_time, "End time is the same")

    def test_late_overlap(self):
        """ Tests adding SpotAvailableHours with a start time within current hours, but an end time later than the current open hours.
        """
        hours1 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="09:00", end_time="12:00")
        hours2 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="10:00", end_time="14:00")

        # creating hours2 should get those times merged into hours1
        hours_obj_count = self.spot.spotavailablehours_set.values_list().count()
        self.assertEquals(hours_obj_count, 1, "Only one SpotAvailableHours object")

        # check to see that start and end times are correct
        new_hours = self.spot.spotavailablehours_set.all()[0]
        self.assertEquals(hours1.start_time, new_hours.start_time, "Start time is the same")
        self.assertEquals(hours2.end_time, new_hours.end_time, "End time is the same")

    def test_total_overlap(self):
        """ Tests adding SpotAvailableHours with an earlier start time and a later end time.
        """
        hours1 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="09:00", end_time="12:00")
        hours2 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="07:00", end_time="14:00")

        # creating hours2 should get those times merged into hours1
        hours_obj_count = self.spot.spotavailablehours_set.values_list().count()
        self.assertEquals(hours_obj_count, 1, "Only one SpotAvailableHours object")

        # check to see that start and end times are correct
        new_hours = self.spot.spotavailablehours_set.all()[0]
        self.assertEquals(hours2.start_time, new_hours.start_time, "Start time is the same")
        self.assertEquals(hours2.end_time, new_hours.end_time, "End time is the same")

    def test_underlap(self):
        """ Tests adding SpotAvailableHours with a start and end insice of currently open hours.
        """
        hours1 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="08:00", end_time="14:00")
        hours2 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="09:00", end_time="12:00")

        # creating hours2 should get those times merged into hours1
        hours_obj_count = self.spot.spotavailablehours_set.values_list().count()
        self.assertEquals(hours_obj_count, 1, "Only one SpotAvailableHours object")

        # check to see that start and end times are correct
        new_hours = self.spot.spotavailablehours_set.all()[0]
        self.assertEquals(hours1.start_time, new_hours.start_time, "Start time is the same")
        self.assertEquals(hours1.end_time, new_hours.end_time, "End time is the same")

    def test_no_overlap(self):
        """ Tests adding another available hours object that should not get merged into an existing one.
        """
        hours1 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="08:00", end_time="12:00")
        hours2 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="14:00", end_time="18:00")

        # creating hours2 should get those times merged into hours1
        hours_obj_count = self.spot.spotavailablehours_set.values_list().count()
        self.assertEquals(hours_obj_count, 2, "Two SpotAvailableHours objects")

        # check to see that start and end times are correct
        new_hours = self.spot.spotavailablehours_set.all()[0]
        new_hours2 = self.spot.spotavailablehours_set.all()[1]
        self.assertEquals(hours1.start_time, new_hours.start_time, "Start time is the same")
        self.assertEquals(hours1.end_time, new_hours.end_time, "End time is the same")
        self.assertEquals(hours2.start_time, new_hours2.start_time, "Start time is the same")
        self.assertEquals(hours2.end_time, new_hours2.end_time, "End time is the same")

    def test_exact_same_start(self):
        """ Tests adding another available hours object that has the exact same start time as an existing one, but a later end.
        """
        hours1 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="09:00", end_time="12:00")
        hours2 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="09:00", end_time="14:00")

        # creating hours2 should get those times merged into hours1
        hours_obj_count = self.spot.spotavailablehours_set.values_list().count()
        self.assertEquals(hours_obj_count, 1, "Only one SpotAvailableHours object")

        # check to see that start and end times are correct
        new_hours = self.spot.spotavailablehours_set.all()[0]
        self.assertEquals(hours1.start_time, new_hours.start_time, "Start time is the same")
        self.assertEquals(hours2.end_time, new_hours.end_time, "End time is the same")

    def test_exact_same_end(self):
        """ Tests adding another available hours object that has the exact same end time as an existing one, but an earlier start.
        """
        hours1 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="09:00", end_time="14:00")
        hours2 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="08:00", end_time="14:00")

        # creating hours2 should get those times merged into hours1
        hours_obj_count = self.spot.spotavailablehours_set.values_list().count()
        self.assertEquals(hours_obj_count, 1, "Only one SpotAvailableHours object")

        # check to see that start and end times are correct
        new_hours = self.spot.spotavailablehours_set.all()[0]
        self.assertEquals(hours2.start_time, new_hours.start_time, "Start time is the same")
        self.assertEquals(hours1.end_time, new_hours.end_time, "End time is the same")

    def test_exact_same_hours(self):
        """ Tests adding the escact same available hours for a spot.
        """
        hours1 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="09:00", end_time="14:00")
        hours2 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="09:00", end_time="14:00")

        # creating hours2 should get those times merged into hours1
        hours_obj_count = self.spot.spotavailablehours_set.values_list().count()
        self.assertEquals(hours_obj_count, 1, "Only one SpotAvailableHours object")

        # check to see that start and end times are correct
        new_hours = self.spot.spotavailablehours_set.all()[0]
        self.assertEquals(hours1.start_time, new_hours.start_time, "Start time is the same")
        self.assertEquals(hours1.end_time, new_hours.end_time, "End time is the same")

    def test_abutting_hours(self):
        """ Tests windows that are next to each other
        """
        hours1 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="09:00", end_time="14:00")
        hours2 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="14:00", end_time="19:00")

        # creating hours2 should get those times merged into hours1
        hours_obj_count = self.spot.spotavailablehours_set.values_list().count()
        self.assertEquals(hours_obj_count, 1, "Only one SpotAvailableHours object")

        # check to see that start and end times are correct
        new_hours = self.spot.spotavailablehours_set.all()[0]
        self.assertEquals(hours1.start_time, new_hours.start_time, "Start time is the same")
        self.assertEquals(hours2.end_time, new_hours.end_time, "End time is the same")

    def test_almost_abutting_hours(self):
        """ Tests windows that are next to each other
        """
        hours1 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="09:00", end_time="13:59:59")
        hours2 = SpotAvailableHours.objects.create(spot=self.spot, day="m", start_time="14:00", end_time="19:00")

        # creating hours2 should get those times merged into hours1
        hours_obj_count = self.spot.spotavailablehours_set.values_list().count()
        self.assertEquals(hours_obj_count, 2, "two SpotAvailableHours objects")

        # check to see that start and end times are correct
        new_hours = self.spot.spotavailablehours_set.all()[0]
        self.assertEquals(hours1.start_time, new_hours.start_time, "Start time is the same")
        self.assertEquals(hours1.end_time, new_hours.end_time, "End time is the same")

        # check to see that start and end times are correct
        new_hours = self.spot.spotavailablehours_set.all()[1]
        self.assertEquals(hours2.start_time, new_hours.start_time, "Start time is the same")
        self.assertEquals(hours2.end_time, new_hours.end_time, "End time is the same")
