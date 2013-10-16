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

from django.core.files import File
from django.test import TestCase
from os.path import abspath, dirname
from spotseeker_server.models import *

TEST_ROOT = abspath(dirname(__file__))


class SpotModelToStringTests(TestCase):
    def test_spot(self):
        spot = Spot.objects.create(name="This is the test name")

        test_str = "{0}".format(spot)
        self.assertEquals(test_str, "This is the test name", "Proper stringification of Spot objects")

    def test_available_hours(self):
        spot = Spot.objects.create(name="This is the test name")
        hours = SpotAvailableHours.objects.create(spot=spot, day="m", start_time="11:00", end_time="14:00")

        test_str = "{0}".format(hours)
        self.assertEquals(test_str, "This is the test name: m, 11:00:00-14:00:00", "Proper stringification of SpotAvailableHours objects")

    def test_extended_info(self):
        spot = Spot.objects.create(name="This is the test name")
        attr = SpotExtendedInfo(key="has_whiteboards", value="1", spot=spot)

        test_str = "{0}".format(attr)
        self.assertEquals(test_str, "This is the test name[has_whiteboards: 1]", "Proper stringification of SpotExtendedInfo objects")

    def test_image(self):
        spot = Spot.objects.create(name="This is the test name")
        f = open("%s/resources/test_gif.gif" % TEST_ROOT)
        gif = SpotImage.objects.create(description="This is the GIF test", spot=spot, image=File(f))

        test_str = "{0}".format(gif)
        self.assertEquals(test_str, "This is the GIF test", "Proper stringification of SpotImage objects")
