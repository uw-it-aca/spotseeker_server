""" Copyright 2016 UW Information Technology, University of Washington
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
from spotseeker_server.models import Spot, SpotExtendedInfo
import simplejson as json
from django.test.utils import override_settings
from mock import patch
from datetime import datetime, timedelta
from django.utils import timezone


@override_settings(
    SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
    SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.'
                         'DefaultSpotForm')
@override_settings(
    SPOTSEEKER_SPOTEXTENDEDINFO_FORM='spotseeker_server.default_forms.spot.'
                                     'DefaultSpotExtendedInfoForm')
@override_settings(SPOTSEEKER_AUTH_ADMINS=('demo_user',))
class FuturePUTTest(TestCase):
    """ Tests updating future Spot Extended information via PUT.
    """

    def setUp(self):
        spot = Spot.objects.create(name="This is for testing future PUT")
        spot.save()
        self.spot = spot

        url = '/api/v1/spot/{0}'.format(self.spot.pk)
        self.url = url

        now = timezone.now()
        last_week = now - timedelta(days=7)
        yesterday = now - timedelta(days=1)

        next_week = now + timedelta(days=7)
        tomorrow = now + timedelta(days=1)

        self.now = now
        self.last_week = last_week
        self.yesterday = yesterday
        self.next_week = next_week
        self.tomorrow = tomorrow

    def test_future_without_dates(self):
        c = Client()

        response = c.get(self.url)
        etag = response["ETag"]
        data = {"name": self.spot.name,
                "location": {"latitude": 55, "longitude": 30},
                "future_extended_info": [
                    {"future_key1": "future_value1"}
                 ]
                }
        response = c.put(self.url,
                         json.dumps(data),
                         content_type="application/json",
                         If_Match=etag)

        response = c.get(self.url)
        data = json.loads(response.content)
        self.assertEquals(data["extended_info"]["future_key1"],
                          "future_value1")

    def test_future_with_start(self):
        c = Client()

        response = c.get(self.url)
        etag = response["ETag"]
        data = {"name": self.spot.name,
                "location": {"latitude": 55, "longitude": 30},
                "future_extended_info": [
                    {"future_key1": "future_value1",
                     "valid_on": self.tomorrow.isoformat()}
                 ]
                }
        response = c.put(self.url,
                         json.dumps(data),
                         content_type="application/json",
                         If_Match=etag)

        response = c.get(self.url)
        data = json.loads(response.content)
        fei0 = data["future_extended_info"][0]
        self.assertEquals(fei0["future_key1"], "future_value1")
        self.assertEquals(fei0["valid_on"], self.tomorrow.isoformat())
        self.assertEquals(fei0["valid_until"], None)

    def test_future_with_end(self):
        c = Client()

        response = c.get(self.url)
        etag = response["ETag"]
        data = {"name": self.spot.name,
                "location": {"latitude": 55, "longitude": 30},
                "future_extended_info": [
                    {"future_key1": "future_value1",
                     "valid_until": self.tomorrow.isoformat()}
                 ]
                }
        response = c.put(self.url,
                         json.dumps(data),
                         content_type="application/json",
                         If_Match=etag)

        response = c.get(self.url)
        data = json.loads(response.content)
        fei0 = data["future_extended_info"][0]
        self.assertEquals(fei0["future_key1"], "future_value1")
        self.assertEquals(fei0["valid_until"], self.tomorrow.isoformat())
        self.assertEquals(fei0["valid_on"], None)

    def test_future_with_full_range(self):
        c = Client()

        response = c.get(self.url)
        etag = response["ETag"]
        data = {"name": self.spot.name,
                "location": {"latitude": 55, "longitude": 30},
                "future_extended_info": [
                    {"future_key1": "future_value1",
                     "valid_on": self.tomorrow.isoformat(),
                     "valid_until": self.next_week.isoformat()}
                 ]
                }
        response = c.put(self.url,
                         json.dumps(data),
                         content_type="application/json",
                         If_Match=etag)

        response = c.get(self.url)
        data = json.loads(response.content)
        fei0 = data["future_extended_info"][0]
        self.assertEquals(fei0["future_key1"], "future_value1")
        self.assertEquals(fei0["valid_on"], self.tomorrow.isoformat())
        self.assertEquals(fei0["valid_until"], self.next_week.isoformat())

    def test_future_range_plus_default(self):
        c = Client()

        response = c.get(self.url)
        etag = response["ETag"]
        data = {"name": self.spot.name,
                "location": {"latitude": 55, "longitude": 30},
                "extended_info": {"future_key1": "all-time-value"},
                "future_extended_info": [
                    {"future_key1": "future_value2",
                     "valid_on": self.tomorrow.isoformat(),
                     "valid_until": self.next_week.isoformat()}
                 ]
                }
        response = c.put(self.url,
                         json.dumps(data),
                         content_type="application/json",
                         If_Match=etag)

        response = c.get(self.url)
        data = json.loads(response.content)
        fei0 = data["future_extended_info"][0]
        self.assertEquals(data["extended_info"]["future_key1"],
                          "all-time-value")
        self.assertEquals(fei0["future_key1"], "future_value2")
        self.assertEquals(fei0["valid_on"], self.tomorrow.isoformat())
        self.assertEquals(fei0["valid_until"], self.next_week.isoformat())

    def test_future_range_plus_default_replacing(self):
        c = Client()

        response = c.get(self.url)
        etag = response["ETag"]
        data = {"name": self.spot.name,
                "location": {"latitude": 55, "longitude": 30},
                "extended_info": {"future_key1": "all-time-value-2"},
                "future_extended_info": [
                    {"future_key1": "future_value3",
                     "valid_on": self.tomorrow.isoformat(),
                     "valid_until": self.next_week.isoformat()}
                 ]
                }
        response = c.put(self.url,
                         json.dumps(data),
                         content_type="application/json",
                         If_Match=etag)

        response = c.get(self.url)
        data = json.loads(response.content)

        fei0 = data["future_extended_info"][0]
        self.assertEquals(data["extended_info"]["future_key1"],
                          "all-time-value-2")
        self.assertEquals(fei0["future_key1"], "future_value3")
        self.assertEquals(fei0["valid_on"], self.tomorrow.isoformat())
        self.assertEquals(fei0["valid_until"], self.next_week.isoformat())

        response = c.get(self.url)
        etag = response["ETag"]
        data = {"name": self.spot.name,
                "location": {"latitude": 55, "longitude": 30},
                "extended_info": {"future_key1": "all-time-value-3"},
                "future_extended_info": [
                    {"future_key1": "future_value3",
                     "valid_on": self.tomorrow.isoformat(),
                     "valid_until": self.next_week.isoformat()}
                 ]

                }
        response = c.put(self.url,
                         json.dumps(data),
                         content_type="application/json",
                         If_Match=etag)

        response = c.get(self.url)
        etag = response["ETag"]
        data = {"name": self.spot.name,
                "location": {"latitude": 55, "longitude": 30},
                "extended_info": {"future_key1": "all-time-value-3"},
                "future_extended_info": [
                    {"future_key1": "future_value4",
                     "valid_on": self.tomorrow.isoformat(),
                     "valid_until": self.next_week.isoformat()}
                 ]
                }
        response = c.put(self.url,
                         json.dumps(data),
                         content_type="application/json",
                         If_Match=etag)

        response = c.get(self.url)
        data = json.loads(response.content)
        self.assertEquals(data["extended_info"]["future_key1"],
                          "all-time-value-3")

        fei0 = data["future_extended_info"][0]
        self.assertEquals(fei0["future_key1"], "future_value4")
        self.assertEquals(fei0["valid_on"], self.tomorrow.isoformat())
        self.assertEquals(fei0["valid_until"], self.next_week.isoformat())

    def test_future_range_plus_default_removal(self):
        c = Client()

        response = c.get(self.url)
        etag = response["ETag"]
        data = {"name": self.spot.name,
                "location": {"latitude": 55, "longitude": 30},
                "extended_info": {"future_key1": "all-time-value"},
                "future_extended_info": [
                    {"future_key1": "future_value2",
                     "valid_on": self.tomorrow.isoformat(),
                     "valid_until": self.next_week.isoformat()}
                 ]
                }
        response = c.put(self.url,
                         json.dumps(data),
                         content_type="application/json",
                         If_Match=etag)

        response = c.get(self.url)
        data = json.loads(response.content)
        self.assertEquals(data["extended_info"]["future_key1"],
                          "all-time-value")
        fei0 = data["future_extended_info"][0]
        self.assertEquals(fei0["future_key1"], "future_value2")
        self.assertEquals(fei0["valid_on"], self.tomorrow.isoformat())
        self.assertEquals(fei0["valid_until"], self.next_week.isoformat())

        response = c.get(self.url)
        etag = response["ETag"]
        data = {"name": self.spot.name,
                "location": {"latitude": 55, "longitude": 30},
                }
        response = c.put(self.url,
                         json.dumps(data),
                         content_type="application/json",
                         If_Match=etag)

        response = c.get(self.url)
        data = json.loads(response.content)
        self.assertEquals(data["extended_info"], {})
        self.assertEquals(data["future_extended_info"], [])

    def tearDown(self):
        self.spot.delete()
