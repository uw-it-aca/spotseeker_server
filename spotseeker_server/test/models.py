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
from datetime import datetime, timedelta
from django.utils import timezone
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
        spot = Spot.objects.create(name="This is the test name")
        f = open("%s/resources/test_gif.gif" % TEST_ROOT)
        gif = SpotImage.objects.create(
            description="This is the GIF test",
            spot=spot,
            image=File(f))

        test_str = "{0}".format(gif)
        self.assertEqual(test_str, "This is the GIF test")


class SpotExtendedInfoTests(TestCase):
    def setUp(self):
        s = Spot()

        ei1 = SpotExtendedInfo()
        ei1.spot = s
        ei1.key = "k1"
        ei1.value = "v1"
        ei1.valid_on = None
        ei1.valid_until = None

        ei2 = SpotExtendedInfo()
        ei2.spot = s
        ei2.key = "k2"
        ei2.value = "v2"
        ei2.valid_on = None
        ei2.valid_until = None

        self.ei1 = ei1
        self.ei2 = ei2

    def test_none_v_left_def(self):
        self.ei1.valid_on = None
        self.ei1.valid_until = None

        self.ei2.valid_on = timezone.now() - timedelta(days=1)
        self.ei2.valid_until = None

        ei_list = [self.ei2, self.ei1]
        ei_list.sort(SpotExtendedInfo.sort_method)

        self.assertEqual(ei_list[0].key, "k1")
        self.assertEqual(ei_list[1].key, "k2")

    def test_little_left_vs_big(self):
        self.ei1.valid_on = timezone.now() - timedelta(days=2)
        self.ei1.valid_until = None

        self.ei2.valid_on = timezone.now() - timedelta(days=1)
        self.ei2.valid_until = None

        ei_list = [self.ei2, self.ei1]
        ei_list.sort(SpotExtendedInfo.sort_method)

        self.assertEqual(ei_list[0].key, "k1")
        self.assertEqual(ei_list[1].key, "k2")

    def test_left_v_right(self):
        self.ei1.valid_on = timezone.now() - timedelta(days=2)
        self.ei1.valid_until = None

        self.ei2.valid_on = None
        self.ei2.valid_until = timezone.now() + timedelta(days=1)

        ei_list = [self.ei2, self.ei1]
        ei_list.sort(SpotExtendedInfo.sort_method)

        self.assertEqual(ei_list[0].key, "k1")
        self.assertEqual(ei_list[1].key, "k2")

    def test_little_v_big_right(self):
        self.ei1.valid_on = None
        self.ei1.valid_until = timezone.now() + timedelta(days=2)

        self.ei2.valid_on = None
        self.ei2.valid_until = timezone.now() + timedelta(days=1)

        ei_list = [self.ei2, self.ei1]
        ei_list.sort(SpotExtendedInfo.sort_method)

        self.assertEqual(ei_list[0].key, "k1")
        self.assertEqual(ei_list[1].key, "k2")

    def test_right_vs_fully_defined(self):
        self.ei1.valid_on = None
        self.ei1.valid_until = timezone.now() + timedelta(days=1)

        self.ei2.valid_on = timezone.now() - timedelta(days=1)
        self.ei2.valid_until = timezone.now() + timedelta(days=2)

        ei_list = [self.ei2, self.ei1]
        ei_list.sort(SpotExtendedInfo.sort_method)

        self.assertEqual(ei_list[0].key, "k1")
        self.assertEqual(ei_list[1].key, "k2")

    def test_big_vs_small_full_right_side(self):
        self.ei1.valid_on = timezone.now() - timedelta(days=1)
        self.ei1.valid_until = timezone.now() + timedelta(days=2)

        self.ei2.valid_on = timezone.now() - timedelta(days=1)
        self.ei2.valid_until = timezone.now() + timedelta(days=1)

        ei_list = [self.ei2, self.ei1]
        ei_list.sort(SpotExtendedInfo.sort_method)

        self.assertEqual(ei_list[0].key, "k1")
        self.assertEqual(ei_list[1].key, "k2")

    def test_big_vs_small_full_left_side(self):
        now = timezone.now()
        self.ei1.valid_on = timezone.now() - timedelta(days=2)
        self.ei1.valid_until = now + timedelta(days=1)

        self.ei2.valid_on = timezone.now() - timedelta(days=1)
        self.ei2.valid_until = now + timedelta(days=1)

        ei_list = [self.ei2, self.ei1]
        ei_list.sort(SpotExtendedInfo.sort_method)

        self.assertEqual(ei_list[0].key, "k1")
        self.assertEqual(ei_list[1].key, "k2")

    def test_key_sort(self):
        now = timezone.now()
        self.ei1.valid_on = now - timedelta(days=1)
        self.ei1.valid_until = now + timedelta(days=1)

        self.ei2.valid_on = now - timedelta(days=1)
        self.ei2.valid_until = now + timedelta(days=1)
        self.ei2.key = "k2"

        ei_list = [self.ei2, self.ei1]
        ei_list.sort(SpotExtendedInfo.sort_method)

        self.assertEqual(ei_list[0].value, "v1")
        self.assertEqual(ei_list[1].value, "v2")

    def test_value_sort(self):
        now = timezone.now()
        self.ei1.valid_on = now - timedelta(days=1)
        self.ei1.valid_until = now + timedelta(days=1)

        self.ei2.valid_on = now - timedelta(days=1)
        self.ei2.key = "k1"
        self.ei2.valid_until = now + timedelta(days=1)

        ei_list = [self.ei2, self.ei1]
        ei_list.sort(SpotExtendedInfo.sort_method)

        self.assertEqual(ei_list[0].value, "v1")
        self.assertEqual(ei_list[1].value, "v2")

    def test_extended_info_sorting(self):
        s = Spot()
        now = timezone.now()

        ei1 = SpotExtendedInfo()
        ei1.spot = s
        ei1.key = "k1"
        ei1.value = "v1"
        ei1.valid_on = None
        ei1.valid_until = None

        ei2 = SpotExtendedInfo()
        ei2.spot = s
        ei2.key = "k2"
        ei2.value = "v2"
        ei2.valid_on = now - timedelta(days=1)
        ei2.valid_until = None

        ei3 = SpotExtendedInfo()
        ei3.spot = s
        ei3.key = "k3"
        ei3.value = "v3"
        ei3.valid_on = None
        ei3.valid_until = now + timedelta(days=1)

        ei4 = SpotExtendedInfo()
        ei4.spot = s
        ei4.key = "k4"
        ei4.value = "v4"
        ei4.valid_on = now - timedelta(days=2)
        ei4.valid_until = now + timedelta(days=2)

        ei5 = SpotExtendedInfo()
        ei5.spot = s
        ei5.key = "k5"
        ei5.value = "v5"
        ei5.valid_on = now - timedelta(days=1)
        ei5.valid_until = now + timedelta(days=1)

        ei6 = SpotExtendedInfo()
        ei6.spot = s
        ei6.key = "k6"
        ei6.value = "v6"
        ei6.valid_on = now - timedelta(days=1)
        ei6.valid_until = now + timedelta(days=1)

        ei_list = [ei3, ei2, ei4, ei1, ei6, ei5]

        ei_list.sort(SpotExtendedInfo.sort_method)

        self.assertEquals(ei_list[0].key, "k1")
        self.assertEquals(ei_list[1].key, "k2")
        self.assertEquals(ei_list[2].key, "k3")
        self.assertEquals(ei_list[3].key, "k4")
        self.assertEquals(ei_list[4].key, "k5")
        self.assertEquals(ei_list[5].key, "k6")
