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
from mock import patch
from spotseeker_server import models
import json
import time


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
class HoursRangeTest(TestCase):
    """ Tests searches for spots that are open anywhere
        within a range of hours.
    """

    def setUp(self):
        """ Creates a spot that is open between 10:00:00 and
        13:00:00 on Wednesday.
        """
        self.now = datetime(16, 2, 3, 9, 0, 0)
        spot_open = datetime.time(self.now + timedelta(hours=1))
        spot_close = datetime.time(self.now + timedelta(hours=4))

        self.spot1 = models.Spot.objects.create(
            name="Spot that opens at {0}:{1} and closes at {2}:{3}".format(
                spot_open.hour,
                spot_open.minute,
                spot_close.hour,
                spot_close.minute))
        day_lookup = ["su", "m", "t", "w", "th", "f", "sa"]
        self.today = day_lookup[3]

        for i in [1, 2, 3, 4, 5]:
            models.SpotAvailableHours.objects.create(
                spot=self.spot1,
                day=day_lookup[i],
                start_time=spot_open,
                end_time=spot_close)

        spot_open = datetime.time(self.now + timedelta(hours=3))
        spot_close = datetime.time(self.now + timedelta(hours=8))

        self.spot2 = models.Spot.objects.create(
            name="Spot that opens at {0}:{1} and closes at {2}:{3}".format(
                spot_open.hour,
                spot_open.minute,
                spot_close.hour,
                spot_close.minute
            )
        )

        for i in [1, 2, 3, 4, 5]:
            models.SpotAvailableHours.objects.create(
                spot=self.spot2,
                day=day_lookup[i],
                start_time=spot_open,
                end_time=spot_close
            )

        spot_open = datetime.time(self.now + timedelta(hours=10))
        spot_close = datetime.time(self.now + timedelta(hours=14))

        self.spot3 = models.Spot.objects.create(
            name="Spot that opens at {0}:{1} and closes at {2}:{3}".format(
                spot_open.hour,
                spot_open.minute,
                spot_close.hour,
                spot_close.minute
            )
        )

        for i in [1, 2, 3, 4, 5]:
            models.SpotAvailableHours.objects.create(
                spot=self.spot3,
                day=day_lookup[i],
                start_time=spot_open,
                end_time=spot_close
            )

        spot_open_today = datetime.time(self.now + timedelta(hours=10))
        spot_close_today = datetime.time(
            self.now + timedelta(hours=14, minutes=59))
        spot_open_tomorrow = datetime.time(self.now - timedelta(hours=9))
        spot_close_tomorrow = datetime.time(self.now - timedelta(hours=2))

        self.today = day_lookup[3]
        self.tomorrow = day_lookup[4]

        self.spot4 = models.Spot.objects.create(
            name="Spot opens {4} at {0}:{1} and closes {5} at {2}:{3}".format(
                spot_open_today.hour,
                spot_open_today.minute,
                spot_close_tomorrow.hour,
                spot_close_tomorrow.minute,
                self.today,
                self.tomorrow))
        day_lookup = ["su", "m", "t", "w", "th", "f", "sa"]

        for i in [1, 2, 3, 4, 5]:
            models.SpotAvailableHours.objects.create(
                spot=self.spot4,
                day=day_lookup[i],
                start_time=spot_open_today,
                end_time=spot_close_today
            )

            models.SpotAvailableHours.objects.create(
                spot=self.spot4,
                day=day_lookup[i+1],
                start_time=spot_open_tomorrow,
                end_time=spot_close_tomorrow
            )

        spot_open = datetime.time(self.now - timedelta(hours=9))
        spot_close = datetime.time(self.now - timedelta(hours=2))

        self.spot5 = models.Spot.objects.create(
            name="Spot that opens at {0}:{1} and closes at {2}:{3}".format(
                spot_open.hour,
                spot_open.minute,
                spot_close.hour,
                spot_close.minute
            )
        )

        for i in [1, 2, 3, 4, 5]:
            models.SpotAvailableHours.objects.create(
                spot=self.spot5,
                day=day_lookup[i],
                start_time=spot_open,
                end_time=spot_close
            )

        self.day_dict = {"su": "Sunday",
                         "m": "Monday",
                         "t": "Tuesday",
                         "w": "Wednesday",
                         "th": "Thursday",
                         "f": "Friday",
                         "sa": "Saturday", }

    def test_spot_opening_within_range(self):
        """ Tests search for a spot that opens during the search range.
        This should return spot 1. Search range: today 7:00 - 11:00
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
                "/api/v1/spot",
                {'fuzzy_hours_start': start_query,
                 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertTrue(self.spot1.json_data_structure() in spots)
            self.assertFalse(self.spot2.json_data_structure() in spots)
            self.assertFalse(self.spot3.json_data_structure() in spots)
            self.assertFalse(self.spot4.json_data_structure() in spots)
            self.assertFalse(self.spot5.json_data_structure() in spots)

    def test_spot_closing_within_range(self):
        """ Tests search for a spot that closes during the search range.
        Search range: today 11:00 - 14:00
        This should return spot 1 and 2, we don't test for 2 because it's
        returned for a valid reason that is outside the scope of this test.
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
                "/api/v1/spot",
                {'fuzzy_hours_start': start_query,
                 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertTrue(self.spot1.json_data_structure() in spots)
            # Don't assert on spot2, see above docstring.
            self.assertFalse(self.spot3.json_data_structure() in spots)
            self.assertFalse(self.spot4.json_data_structure() in spots)
            self.assertFalse(self.spot5.json_data_structure() in spots)

    def test_spot_open_hours_span_entire_range(self):
        """ Tests search for a spot that opens before the search start time and
        closes after the search end time on the same day.
        Search range: 13:00 15:00 . This should return spot 2.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now + timedelta(hours=4))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            end_query_time = datetime.time(self.now + timedelta(hours=6))
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.today]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot",
                {'fuzzy_hours_start': start_query,
                 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(self.spot1.json_data_structure() in spots)
            self.assertTrue(self.spot2.json_data_structure() in spots)
            self.assertFalse(self.spot3.json_data_structure() in spots)
            self.assertFalse(self.spot4.json_data_structure() in spots)
            self.assertFalse(self.spot5.json_data_structure() in spots)

    def test_open_close_in_range(self):
        """ Tests search for a spot that opens and closes within the
            search range. Search range: today 8:00 - 14:00
            This should return spot 1 and 2, but don't assert spot2 as it
            is returned for a valid reason outside of the scope of this test.
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
                "/api/v1/spot",
                {'fuzzy_hours_start': start_query,
                 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertTrue(self.spot1.json_data_structure() in spots)
            # Don't assert spot2, see reason in docstring above
            self.assertFalse(self.spot3.json_data_structure() in spots)
            self.assertFalse(self.spot4.json_data_structure() in spots)
            self.assertFalse(self.spot5.json_data_structure() in spots)

    def test_open_within_range_and_close_within_range_next_day(self):
        """ Tests search for a spot that opens within the search range
            and closes within the search range the next day.
            Search range: today 18:00 - tomorrow 9:00
            This should return spot 3, 4, and 5, but don't assert spot3 as it
            is returned for a valid reason outside of the scope of this test.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now + timedelta(hours=9))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            end_query_time = datetime.time(self.now)
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.tomorrow]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot",
                {'fuzzy_hours_start': start_query,
                 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(self.spot1.json_data_structure() in spots)
            self.assertFalse(self.spot2.json_data_structure() in spots)
            # Don't assert spot3, see reason in docstring above
            self.assertTrue(self.spot4.json_data_structure() in spots)
            self.assertTrue(self.spot5.json_data_structure() in spots)

    def test_open_and_close_before_range(self):
        """ Tests search for a spot that opens and closes before the
        search range. Search range: 14:00 - 17:00
        This should NOT return any spots.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now + timedelta(hours=5))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            end_query_time = datetime.time(self.now + timedelta(hours=8))
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.today]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot",
                {'fuzzy_hours_start': start_query,
                 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(self.spot1.json_data_structure() in spots)
            self.assertFalse(self.spot2.json_data_structure() in spots)
            self.assertFalse(self.spot3.json_data_structure() in spots)
            self.assertFalse(self.spot4.json_data_structure() in spots)
            self.assertFalse(self.spot5.json_data_structure() in spots)

    def test_open_and_close_after_range(self):
        """ Tests search for a spot that opens and closes after the search
       range. Search range: 10:00 - 11:00
        This should return spot 1, but don't assert as it satisfies a valid
        case outside the scope of this test.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now + timedelta(hours=1))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            end_query_time = datetime.time(self.now + timedelta(hours=2))
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.today]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot",
                {'fuzzy_hours_start': start_query,
                 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            # don't assert spot1, see above docstring.
            self.assertFalse(self.spot2.json_data_structure() in spots)
            self.assertFalse(self.spot3.json_data_structure() in spots)
            self.assertFalse(self.spot4.json_data_structure() in spots)
            self.assertFalse(self.spot5.json_data_structure() in spots)

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
        """ Tests search for a spot that closes at exactly the time the
        search range begins. Search range: 13:00 - 14:00
        This should return spot 2, but don't assert as it matches a valid
        search outside the scope of this test.
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
                "/api/v1/spot",
                {'fuzzy_hours_start': start_query,
                 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(self.spot1.json_data_structure() in spots)
            # don't assert spot2, see above docstring
            self.assertFalse(self.spot3.json_data_structure() in spots)
            self.assertFalse(self.spot4.json_data_structure() in spots)
            self.assertFalse(self.spot5.json_data_structure() in spots)

    def test_opens_at_end(self):
        """ Tests search for a spot that opens at exactly the time
        the search range ends. Search range: 4:00 - 10:00
        This should NOT return the spot.
        Returns spot5 but don't assert against spot5 as it is returned as a
        valid result but for reasons out of scope of this test.
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
                "/api/v1/spot",
                {'fuzzy_hours_start': start_query,
                 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(self.spot1.json_data_structure() in spots)
            self.assertFalse(self.spot2.json_data_structure() in spots)
            self.assertFalse(self.spot3.json_data_structure() in spots)
            # Don't assert spot5, see docstring above

    def test_open_within_range_and_close_outside_range_next_day(self):
        """ Tests a search range that spans midnight. This should return
            spot 3, 4, and 5. Search range: today 18:00 - tomorrow 2:00
            Don't assert against spot3 as it is returned as a
            valid result but for reasons out of scope of this test.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now + timedelta(hours=9))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            end_query_time = datetime.time(self.now - timedelta(hours=7))
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.tomorrow]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot",
                {'fuzzy_hours_start': start_query,
                 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(self.spot1.json_data_structure() in spots)
            self.assertFalse(self.spot2.json_data_structure() in spots)
            # Don't assert spot3, see docstring above
            self.assertTrue(self.spot4.json_data_structure() in spots)
            self.assertTrue(self.spot5.json_data_structure() in spots)

    def test_open_outside_range_and_close_within_range_next_day(self):
        """ Tests a search range that spans midnight. This should return
            spot 3, 4, and 5. Search range: today 20:00 - tomorrow 9:00
            Don't assert against spot3 and spot5 as it is returned as a
            valid result but for reasons out of scope of this test.
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now + timedelta(hours=11))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            end_query_time = datetime.time(self.now)
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.tomorrow]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot",
                {'fuzzy_hours_start': start_query,
                 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(self.spot1.json_data_structure() in spots)
            self.assertFalse(self.spot2.json_data_structure() in spots)
            # Don't assert spot3, see docstring above
            self.assertTrue(self.spot4.json_data_structure() in spots)
            # Don't assert spot5, see docstring above



    def test_span_late_night(self):
        """ Tests a search range where the spot's open time is before the
            start on one day, and the close time is beyond the end of
            range on the next day. Search range: today 20:00 - tomorrow 2:00
        """
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            start_query_time = datetime.time(self.now + timedelta(hours=11))
            start_query_time = start_query_time.strftime("%H:%M")
            start_query_day = self.day_dict[self.today]
            start_query = "%s,%s" % (start_query_day, start_query_time)

            end_query_time = datetime.time(self.now - timedelta(hours=7))
            end_query_time = end_query_time.strftime("%H:%M")
            end_query_day = self.day_dict[self.tomorrow]
            end_query = "%s,%s" % (end_query_day, end_query_time)

            client = Client()
            response = client.get(
                "/api/v1/spot",
                {'fuzzy_hours_start': start_query,
                 'fuzzy_hours_end': end_query})
            spots = json.loads(response.content)

            self.assertEqual(response.status_code, 200)
            self.assertFalse(self.spot1.json_data_structure() in spots)
            self.assertFalse(self.spot2.json_data_structure() in spots)
            # Don't assert spot3, see docstring above
            self.assertTrue(self.spot4.json_data_structure() in spots)
            # Don't assert spot5, see docstring above
        pass

    def tearDown(self):
        self.spot1.delete()
        self.spot2.delete()
        self.spot3.delete()
        self.spot4.delete()
