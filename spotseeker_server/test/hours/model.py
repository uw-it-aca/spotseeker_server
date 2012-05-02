from django.utils import unittest
from django.conf import settings
import datetime
from spotseeker_server.models import Spot, SpotAvailableHours


class SpotHoursModelTest(unittest.TestCase):
    """ Tests for Spot AvailableHours.
    """
    settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok';
    def test_startMatchesEnd(self):
        """ Tests that a Spot's AvailableHours cannot have zero length.
        """
        spot = Spot.objects.create(name='testing hours')
        try:
            hours = SpotAvailableHours.objects.create(day="m", spot=spot, start_time="01:30",  end_time="01:30")
        except Exception as e:
            self.assertEquals(e[0], "Invalid time range - start time must be before end time", "Got an error trying to save a time range with no time in it")

    def test_startAfterEnd(self):
        """ Tests that a Spot's AvailableHours cannot end before they begin.
        """
        spot = Spot.objects.create(name='testing hours')
        try:
            hours = SpotAvailableHours.objects.create(day="m", spot=spot, start_time="01:40",  end_time="01:30")
        except Exception as e:
            self.assertEquals(e[0], "Invalid time range - start time must be before end time", "Got an error trying to save a time range with no time in it")

    def test_properRange(self):
        """ Tests that having AvailableHours with a start time before the end time saves properly.
        """
        spot = Spot.objects.create(name='testing hours')
        hours = SpotAvailableHours.objects.create(day="m", spot=spot, start_time="01:30",  end_time="01:40")

        self.assertEquals(hours.start_time,  datetime.time(1, 30), "ok")
        self.assertEquals(hours.end_time,  datetime.time(1, 40), "ok")
        self.assertEquals(hours.day,  "m", "ok")

    def test_missingStart(self):
        """ Tests that AvailableHours cannot be created with no start time.
        """
        spot = Spot.objects.create(name='testing hours')
        has_error = False
        try:
            hours = SpotAvailableHours.objects.create(spot=spot, day="m",  end_time="01:30")
        except:
            has_error = True

        self.assertEquals(has_error, True, "Doesn't allow hours to be stored without a start time")

    def test_missingEnd(self):
        """ Tests that AvailableHours cannot be created with no end time.
        """
        spot = Spot.objects.create(name='testing hours')
        has_error = False
        try:
            hours = SpotAvailableHours.objects.create(spot=spot, day="m", start_time="01:30")
        except:
            has_error = True

        self.assertEquals(has_error, True, "Doesn't allow hours to be stored without an end time")

    def test_missingHours(self):
        """ Tests that AvailableHourse cannot be created with out a time range.
        """
        spot = Spot.objects.create(name='testing hours')
        has_error = False
        try:
            hours = SpotAvailableHours.objects.create(spot=spot, day="m")
        except:
            has_error = True

        self.assertEquals(has_error, True, "Doesn't allow hours to be stored without hours")

    def test_missingDay(self):
        """ Tests that AvailableHours cannot be created without a day of the week.
        """
        spot = Spot.objects.create(name='testing hours')
        has_error = False
        try:
            hours = SpotAvailableHours.objects.create(spot=spot, start_time="01:30", end_time="02:30")
        except:
            has_error = True

        self.assertEquals(has_error, True, "Doesn't allow hours to be stored without a day")

    def test_invalidDay(self):
        """ Tests that AvailableHours cannot be created with a day that doesn't exist as a day of the week.
        """
        spot = Spot.objects.create(name='testing hours')
        has_error = False
        try:
            hours = SpotAvailableHours.objects.create(spot=spot, day="Fail_day", start_time="01:30", end_time="02:30")
        except Exception as e:
            has_error = True

        self.assertEquals(has_error, True, "Doesn't allow hours to be stored with an invalid day")
