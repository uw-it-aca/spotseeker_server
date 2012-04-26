
from django.core.files import File
from django.utils import unittest
from spotseeker_server.models import *
from os.path import abspath, dirname

TEST_ROOT = abspath(dirname(__file__))

class SpotModelToStringTests(unittest.TestCase):
    def test_spot(self):
        spot = Spot.objects.create(name="This is the test name")

        test_str = "{0}".format(spot)
        self.assertEquals(test_str, "This is the test name", "Proper stringification of Spot objects")

    def test_available_hours(self):
        spot = Spot.objects.create(name="This is the test name")
        hours = SpotAvailableHours.objects.create(spot = spot, day = "m", start_time="11:00", end_time="14:00")

        test_str = "{0}".format(hours)
        self.assertEquals(test_str, "m: 11:00:00-14:00:00", "Proper stringification of SpotAvailableHours objects")

    def test_extended_info(self):
        spot = Spot.objects.create(name="This is the test name")
        attr = SpotExtendedInfo(key = "has_whiteboards", value = "1", spot = spot)

        test_str = "{0}".format(attr)
        self.assertEquals(test_str, "This is the test name[has_whiteboards: 1]", "Proper stringification of SpotExtendedInfo objects")

    def test_image(self):
        spot = Spot.objects.create(name="This is the test name")
        f = open("%s/resources/test_gif.gif" % TEST_ROOT)
        gif = SpotImage.objects.create( description = "This is the GIF test", spot=spot, image = File(f) )

        test_str = "{0}".format(gif)
        self.assertEquals(test_str, "This is the GIF test", "Proper stringification of SpotImage objects")
