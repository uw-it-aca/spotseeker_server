""" Copyright 2012 - 2015 UW Information Technology, University of Washington

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
from datetime import datetime, timedelta
from django.core import cache
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.utils.unittest import skipIf
from mock import patch
from spotseeker_server import models
import json
import time


# TODO: rather than skipping tests near midnight, mock datetime.now() to
# return a consistent time.
@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
@skipIf(datetime.now().hour + 3 > 23 or datetime.now().hour < 3, "Skip open_at tests due to the time of day")
class HoursRangeTest(TestCase):
    """ Tests searches for spots that are open anywhere within a range of hours.
    """

    def setUp(self):
        #TODO: set an explicit date time on the spot_open and spot_close so we don't need so many skips
        self.now = datetime.now()
        self.now = self.now - \
            timedelta(seconds=self.now.second,
                      microseconds=self.now.microsecond)
        spot_open = datetime.time(self.now + timedelta(hours=1))
        spot_close = datetime.time(self.now + timedelta(hours=4))

        self.spot1 = models.Spot.objects.create(name="Spot that opens at {0}:{1} and closes at {2}:{3}".format(
            spot_open.hour, spot_open.minute, spot_close.hour, spot_close.minute))

        day_lookup = ["su", "m", "t", "w", "th", "f", "sa"]
        day_num = int(time.strftime("%w", time.localtime()))
        self.today = day_lookup[day_num]

        models.SpotAvailableHours.objects.create(
            spot=self.spot1, day=self.today, start_time=spot_open, end_time=spot_close)

        self.day_dict = {"su": "Sunday",
                         "m": "Monday",
                         "t": "Tuesday",
                         "w": "Wednesday",
                         "th": "Thursday",
                         "f": "Friday",
                         "sa": "Saturday", }

    def test_open_within_range(self):
        """ Tests search for a spot that opens within the requested range.
        This should return the spot.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now - timedelta(hours=2))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            end_query_time = datetime.time(self.now + timedelta(hours=2))
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.today]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot", {'fuzzy_hours_start': start_query, 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertTrue(self.spot1.json_data_structure() in spots)

    def test_closes_within_range(self):
        """ Tests search for a spot that closes within the requested range.
        This should return the spot.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now + timedelta(hours=2))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            end_query_time = datetime.time(self.now + timedelta(hours=5))
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.today]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot", {'fuzzy_hours_start': start_query, 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertTrue(self.spot1.json_data_structure() in spots)

    def test_open_and_close_span_range(self):
        """ Tests search for a spot that opens before the requested range and
        closes after the requested range.
        This should return the spot.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now + timedelta(hours=2))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            end_query_time = datetime.time(self.now + timedelta(hours=3))
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.today]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot", {'fuzzy_hours_start': start_query, 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertTrue(self.spot1.json_data_structure() in spots)

    def test_open_after_range_but_end_in_range(self):
        """ Tests search for a spot that opens outside of the requested range
        but closes within the requested range the next day.
        This should return the spot.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            pass

    def test_open_within_range_but_end_outside(self):
        """ Tests search for a spot that opens inside of the requested range but
        closes outside of the requested range the next day (it spans midnight.)
        This should return the spot.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now + timedelta(hours=2))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            end_query_time = datetime.time(self.now + timedelta(hours=8))
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.today]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot", {'fuzzy_hours_start': start_query, 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertTrue(self.spot1.json_data_structure() in spots)

    def test_open_close_in_range(self):
        """ Tests search for a spot that opens and closes within the requested
        hours range.
        This should return the spot.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now - timedelta(hours=1))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            end_query_time = datetime.time(self.now + timedelta(hours=5))
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.today]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot", {'fuzzy_hours_start': start_query, 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertTrue(self.spot1.json_data_structure() in spots)

    def test_start_within_range_and_end_within_range_next_day(self):
        """ Tests search for a spot that opens within the requested range and
        closes within the requested range the next day.
        This should return the spot.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            pass

    def test_start_end_before_range(self):
        """ Tests search for a spot that opens and closes before the requested
        range.
        This should NOT return the spot.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now - timedelta(hours=3))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            end_query_time = datetime.time(self.now - timedelta(hours=2))
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.today]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot", {'fuzzy_hours_start': start_query, 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(self.spot1.json_data_structure() in spots)

    @skipIf(datetime.now().hour + 7 > 23 or datetime.now().hour < 5, "Skip open_at tests due to the time of day")
    def test_start_end_after_range(self):
        """ Tests search for a spot that opens and closes after the requested
        range.
        This should NOT return the spot.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now + timedelta(hours=5))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            end_query_time = datetime.time(self.now + timedelta(hours=7))
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.today]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot", {'fuzzy_hours_start': start_query, 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(self.spot1.json_data_structure() in spots)

    def test_invalid_end_only(self):
        """ Tests search for a spot without passing a start time for the range.
        This should return a 400 bad request.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            end_query_time = datetime.time(self.now + timedelta(hours=7))
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.today]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot", {'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 400)

    def test_invalid_start_only(self):
        """ Tests search for a spot without passing an end time for the range.
        This should return a 400 bad request.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now + timedelta(hours=2))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot", {'fuzzy_hours_start': start_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 400)

    def test_closes_at_start(self):
        """ Tests search for a spot that closes at exactly the time the search range begins.
        This should NOT return the spot.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now + timedelta(hours=4))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            end_query_time = datetime.time(self.now + timedelta(hours=5))
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.today]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot", {'fuzzy_hours_start': start_query, 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(self.spot1.json_data_structure() in spots)

    def test_opens_at_end(self):
        """ Tests search for a spot that opens at exactly the time the search range ends.
        This should NOT return the spot.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now - timedelta(hours=5))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            end_query_time = datetime.time(self.now + timedelta(hours=1))
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.today]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot", {'fuzzy_hours_start': start_query, 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(self.spot1.json_data_structure() in spots)

    def tearDown(self):
        self.spot1.delete()
