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
from spotseeker_server.models import Spot, TrustedOAuthClient
from django.test.client import Client
import re
import simplejson as json
import StringIO
import logging

import hashlib
import time
import random
from contextlib import nested

from oauth_provider.models import Consumer
import oauth2
from django.test.utils import override_settings
from mock import patch
from django.core import cache
from spotseeker_server import models


@override_settings(SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm')
@override_settings(SPOTSEEKER_SPOTEXTENDEDINFO_FORM='spotseeker_server.default_forms.spot.DefaultSpotExtendedInfoForm')
@override_settings(SPOTSEEKER_AUTH_ADMINS=('pmichaud',))
class SpotAuthOAuthLogger(TestCase):
    def setUp(self):
        spot = Spot.objects.create(name="This is for testing the oauth module", capacity=10)
        self.spot = spot
        self.url = "/api/v1/spot/%s" % self.spot.pk

        new_middleware = []
        has_logger = False
        self.original_middleware = settings.MIDDLEWARE_CLASSES
        for middleware in settings.MIDDLEWARE_CLASSES:
            new_middleware.append(middleware)
            if middleware == 'spotseeker_server.logger.oauth.LogMiddleware':
                has_logger = True

        if not has_logger:
            new_middleware.append('spotseeker_server.logger.oauth.LogMiddleware')
        settings.MIDDLEWARE_CLASSES = new_middleware

        self.stream = StringIO.StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.log = logging.getLogger('spotseeker_server.logger.oauth')
        self.log.setLevel(logging.INFO)
        for handler in self.log.handlers:
            self.log.removeHandler(handler)
        self.log.addHandler(self.handler)

    def test_log_value_2_legged(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.oauth'):

                consumer_name = "Test consumer"

                key = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()
                secret = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()

                create_consumer = Consumer.objects.create(name=consumer_name, key=key, secret=secret)

                consumer = oauth2.Consumer(key=key, secret=secret)

                req = oauth2.Request.from_consumer_and_token(consumer, None, http_method='GET', http_url="http://testserver/api/v1/spot/%s" % self.spot.pk)

                oauth_header = req.to_header()

                c = Client()
                response = c.get(self.url, HTTP_AUTHORIZATION=oauth_header['Authorization'])

            with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok'):

                self.handler.flush()
                log_message = self.stream.getvalue()

                matches = re.search('\[.*?\] ([\d]+)\t"(.*?)"\t-\t"GET /api/v1/spot/([\d]+)" ([\d]+) ([\d]+)', log_message)

                consumer_id = int(matches.group(1))
                consumer_name = matches.group(2)
                spot_id = int(matches.group(3))
                status_code = int(matches.group(4))
                response_size = int(matches.group(5))

                self.assertEquals(consumer_id, create_consumer.pk, "Logging correct consumer PK")
                self.assertEquals(consumer_name, create_consumer.name, "Logging correct consumer name")
                self.assertEquals(spot_id, self.spot.pk, "Logging correct uri")
                self.assertEquals(status_code, response.status_code, "Logging correct status_code")
                self.assertEquals(response_size, len(response.content), "Logging correct content size")

    def test_log_trusted_3_legged(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.oauth'):
                consumer_name = "Trusted test consumer"

                key = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()
                secret = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()

                create_consumer = Consumer.objects.create(name=consumer_name, key=key, secret=secret)
                trusted_consumer = TrustedOAuthClient.objects.create(consumer=create_consumer, is_trusted=True)

                consumer = oauth2.Consumer(key=key, secret=secret)

                req = oauth2.Request.from_consumer_and_token(consumer, None, http_method='GET', http_url="http://testserver/api/v1/spot/%s" % self.spot.pk)

                oauth_header = req.to_header()
                c = Client()

                response = c.get(self.url, HTTP_AUTHORIZATION=oauth_header['Authorization'])
                etag = response["ETag"]

                spot_dict = json.loads(response.content)
                spot_dict['name'] = "Failing to modify oauth"
                spot_dict['location'] = {"latitude": 55, "longitude": -30}

                response = c.put(self.url, json.dumps(spot_dict), content_type="application/json", If_Match=etag, HTTP_AUTHORIZATION=oauth_header['Authorization'], HTTP_XOAUTH_USER="pmichaud")
                self.assertEquals(response.status_code, 200, "Accespts a PUT from a trusted oauth client")

            with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok'):

                self.handler.flush()
                log_message = self.stream.getvalue()

                matches = re.search('\n\[.*?\] ([\d]+)\t"(.*?)"\t(.*?)\t"PUT /api/v1/spot/([\d]+)" ([\d]+) ([\d]+)', log_message, re.MULTILINE)

                consumer_id = int(matches.group(1))
                consumer_name = matches.group(2)
                user_name = matches.group(3)
                spot_id = int(matches.group(4))
                status_code = int(matches.group(5))
                response_size = int(matches.group(6))

                self.assertEquals(consumer_id, create_consumer.pk, "Logging correct consumer PK")
                self.assertEquals(consumer_name, create_consumer.name, "Logging correct consumer name")
                self.assertEquals(user_name, "pmichaud", "Logging correct oauth username")
                self.assertEquals(spot_id, self.spot.pk, "Logging correct uri")
                self.assertEquals(status_code, response.status_code, "Logging correct status_code")
                self.assertEquals(response_size, len(response.content), "Logging correct content size")

    def test_invalid(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.oauth'):

                c = Client()
                response = c.get(self.url)

            with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok'):

                self.handler.flush()
                log_message = self.stream.getvalue()

                matches = re.search('\[.*?\] -\t"-"\t-\t"GET /api/v1/spot/([\d]+)" ([\d]+) ([\d]+)', log_message)

                spot_id = int(matches.group(1))
                status_code = int(matches.group(2))
                response_size = int(matches.group(3))

                self.assertEquals(spot_id, self.spot.pk, "Logging correct uri")
                self.assertEquals(status_code, response.status_code, "Logging correct status_code")
                self.assertEquals(response_size, len(response.content), "Logging correct content size")

    def tearDown(self):
        self.log.removeHandler(self.handler)
        self.handler.close()

        settings.MIDDLEWARE_CLASSES = self.original_middleware
