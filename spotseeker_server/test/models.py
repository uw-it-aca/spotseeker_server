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
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from os.path import abspath, dirname
from spotseeker_server.models import *

TEST_ROOT = abspath(dirname(__file__))


class SpotModelToStringTests(TestCase):
    def test_spot(self):
        spot = Spot.objects.create(name="This is the test name")

        test_str = "{0}".format(spot)
        self.assertEqual(test_str, "This is the test name")

    def test_available_hours(self):
        spot = Spot.objects.create(name="This is the test name")
        hours = SpotAvailableHours.objects.create(
            spot=spot,
            day="m",
            start_time="11:00",
            end_time="14:00")

        test_str = "{0}".format(hours)
        self.assertEqual(test_str,
                         "This is the test name: m, 11:00:00-14:00:00")

    def test_extended_info(self):
        spot = Spot.objects.create(name="This is the test name")
        attr = SpotExtendedInfo(key="has_whiteboards", value="1", spot=spot)

        test_str = "{0}".format(attr)
        self.assertEqual(test_str, "This is the test name[has_whiteboards: 1]")

    def test_image(self):
        TEMP_DIR = tempfile.mkdtemp()
        with self.settings(MEDIA_ROOT=TEMP_DIR):
            spot = Spot.objects.create(name="This is the test name")

            gif = SpotImage.objects.create(
                description="This is the GIF test",
                spot=spot,
                image=SimpleUploadedFile(
                    "test_gif.gif",
                    open(
                        "%s/resources/test_gif.gif" % TEST_ROOT, 'rb'
                    ).read(),
                    'image/gif'
                )
            )

            test_str = "{0}".format(gif)
            self.assertEqual(test_str, "This is the GIF test")

        shutil.rmtree(TEMP_DIR)
