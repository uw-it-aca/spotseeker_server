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
from django.test.utils import override_settings
from django.test.client import Client
import simplejson as json
from datetime import datetime, timedelta
import time
from django.test.utils import override_settings
from mock import patch
from spotseeker_server import models
import mock


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
class SpotHoursOpenAtTest(TestCase):
    """ Tests search requests for spots that are open at a particular time.
    """

    @mock.patch('spotseeker_server.views.search.SearchView.get_datetime')
    def test_open_at(self, datetime_mock):
        # Create a spot that isn't open now but will be in an hour.
        spot = models.Spot.objects.create(name="This spot is open later")
        # Setting now to be Wednesday 9:00:00
        now = datetime(16, 2, 3, 9, 0, 0)
        spot_open = datetime.time(now + timedelta(hours=1))
        spot_close = datetime.time(now + timedelta(hours=3))

        day_lookup = ["su", "m", "t", "w", "th", "f", "sa"]
        today = day_lookup[3]

        models.SpotAvailableHours.objects.create(spot=spot,
                                                 day=today,
                                                 start_time=spot_open,
                                                 end_time=spot_close)

        # Mock the call to now() so that the time returned
        # is always 9:00:00
        datetime_mock.return_value = ('w',
                                      datetime(16, 2, 3, 9, 0, 0).time())

        # Verify the spot is closed now
        client = Client()
        response = client.get("/api/v1/spot", {'open_now': True})
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s['id'] == spot.pk:
                spot_returned = True

        self.assertTrue(
            not spot_returned,
            "The spot that is open later is not in the spots open now")

        # Test the spot that is open later
        query_time = datetime.time(now + timedelta(hours=2))
        query_time = query_time.strftime("%H:%M")
        day_dict = {"su": "Sunday",
                    "m": "Monday",
                    "t": "Tuesday",
                    "w": "Wednesday",
                    "th": "Thursday",
                    "f": "Friday",
                    "sa": "Saturday", }
        query_day = day_dict[today]
        query = "%s,%s" % (query_day, query_time)

        response = client.get("/api/v1/spot", {'open_at': query})
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s['id'] == spot.pk:
                spot_returned = True

        self.assertTrue(spot_returned, "Got the spot that is open later")

        # Test that the spot is not returned if we search
        # for open_at == spot_close
        query = "%s,%s" % (query_day, spot_close)

        response = client.get("/api/v1/spot", {'open_at': query})
        spots = json.loads(response.content)

        spot_returned = False

        for s in spots:
            if s['id'] == spot.pk:
                spot_returned = True

        self.assertTrue(
            not spot_returned,
            "The spot that closes at search time is not returned.")
