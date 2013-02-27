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
from django.test.client import Client
from spotseeker_server.models import Spot, SpotAvailableHours
import simplejson as json
from django.test.utils import override_settings
from mock import patch
from django.core import cache
from spotseeker_server import models


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
class SpotHoursGETTest(TestCase):

    def setUp(self):
        spot = Spot.objects.create(name="This spot has available hours")
        # Intentionally out of order - make sure windows are sorted, not just in db happenstance order
        hours2 = SpotAvailableHours.objects.create(spot=spot, day="m", start_time="11:00", end_time="14:00")
        hours1 = SpotAvailableHours.objects.create(spot=spot, day="m", start_time="00:00", end_time="10:00")
        hours3 = SpotAvailableHours.objects.create(spot=spot, day="t", start_time="11:00", end_time="14:00")
        hours4 = SpotAvailableHours.objects.create(spot=spot, day="w", start_time="11:00", end_time="14:00")
        hours5 = SpotAvailableHours.objects.create(spot=spot, day="th", start_time="11:00", end_time="14:00")
        hours6 = SpotAvailableHours.objects.create(spot=spot, day="f", start_time="11:00", end_time="14:00")
        # Saturday is intentionally missing
        hours8 = SpotAvailableHours.objects.create(spot=spot, day="su", start_time="11:00", end_time="14:00")

        self.spot = spot

    def test_hours(self):
        """ Tests that a Spot's available hours can be retrieved successfully.
        """
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            url = "/api/v1/spot/%s" % self.spot.pk
            response = c.get(url)
            spot_dict = json.loads(response.content)

            valid_data = {
                'monday': [["00:00", "10:00"], ["11:00", "14:00"]],
                'tuesday': [["11:00", "14:00"]],
                'wednesday': [["11:00", "14:00"]],
                'thursday': [["11:00", "14:00"]],
                'friday': [["11:00", "14:00"]],
                'saturday': [],
                'sunday': [["11:00", "14:00"]],
            }

            available_hours = spot_dict["available_hours"]
            self.assertEquals(available_hours, valid_data, "Data from the web service matches the data for the spot")
