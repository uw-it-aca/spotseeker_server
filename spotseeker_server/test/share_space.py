""" Copyright 2014 UW Information Technology, University of Washington

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
from django.contrib.auth.models import User
from django.test.utils import override_settings
from spotseeker_server.models import FavoriteSpot, Spot
from mock import patch
from spotseeker_server import models
from django.core import cache
from django.core import mail
import json


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.fake_oauth',
                   SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm',
                   EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',)

class ShareSpaceTest(TestCase):

    def test_basic_oks(self):
        spot = Spot.objects.create(name="This is for testing Sharing 1")

        user, create = User.objects.get_or_create(username='share_test0')

        c = Client()
        c.login(username='share_test0')
        url = "/api/v1/spot/%s/share" % (spot.pk)

        json_data = {
            "to": "vegitron@gmail.com",
            "comment": "This is a sweet space",
            "from": "vegitron@gmail.com",
        }

        response = c.put(url, json.dumps(json_data), content_type="application/json", TESTING_OAUTH_USER="share_test0")



        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, "true", "yup, sent")

        self.assertEquals(mail.outbox[0].to[0], 'vegitron@gmail.com', 'right to')
        mail.outbox = []

    def test_missing_email(self):
        spot = Spot.objects.create(name="This is for testing Sharing 2")

        c = Client()
        url = "/api/v1/spot/%s/share" % (spot.pk)

        json_data = {
            "comment": "This is a sweet space",
        }

        response = c.put(url, json.dumps(json_data), content_type="application/json", TESTING_OAUTH_USER="share_test0")

        self.assertEquals(response.status_code, 400, "400 w/ bad data")

    def test_invalid_email(self):
        spot = Spot.objects.create(name="This is for testing Sharing 2")

        c = Client()
        url = "/api/v1/spot/%s/share" % (spot.pk)

        json_data = {
            "to": "vegitron",
            "comment": "This is a sweet space",
        }

        response = c.put(url, json.dumps(json_data), content_type="application/json", TESTING_OAUTH_USER="share_test0")

        self.assertEquals(response.status_code, 400, "400 w/ bad data")

    def test_missing_comment(self):
        spot = Spot.objects.create(name="This is for testing Sharing 2")

        c = Client()
        url = "/api/v1/spot/%s/share" % (spot.pk)

        json_data = {
            "to": "vegitron@gmail.com",
            "from": "vegitron@gmail.com",
        }

        response = c.put(url, json.dumps(json_data), content_type="application/json", TESTING_OAUTH_USER="share_test0")

        self.assertEquals(response.status_code, 200)


