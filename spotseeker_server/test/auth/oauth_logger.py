# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

try:
    from StringIO import StringIO
except ModuleNotFoundError:
    from io import StringIO

from django.test import TestCase
from django.conf import settings
from spotseeker_server.models import Spot, TrustedOAuthClient
from django.test.client import Client
import re
import simplejson as json
import logging

import hashlib
import time
import random

from oauth_provider.models import Consumer
from django.test.utils import override_settings
from mock import patch
from spotseeker_server import models

from oauthlib import oauth1


@override_settings(
    SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms."
    "spot.DefaultSpotForm",
    SPOTSEEKER_SPOTEXTENDEDINFO_FORM="spotseeker_server.default_forms."
    "spot.DefaultSpotExtendedInfoForm",
    SPOTSEEKER_AUTH_ADMINS=("pmichaud",),
)
class SpotAuthOAuthLogger(TestCase):
    @classmethod
    def setUpTestData(self):
        spot = Spot.objects.create(
            name="This is for testing the oauth module", capacity=10
        )
        self.spot = spot
        self.url = "/api/v1/spot/%s" % self.spot.pk

    def setUp(self):
        new_middleware = []
        has_logger = False
        self.original_middleware = settings.MIDDLEWARE
        for middleware in settings.MIDDLEWARE:
            new_middleware.append(middleware)
            if middleware == "spotseeker_server.logger.oauth.LogMiddleware":
                has_logger = True

        if not has_logger:
            new_middleware.append(
                "spotseeker_server.logger.oauth.LogMiddleware"
            )
        settings.MIDDLEWARE = new_middleware

        self.stream = StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.log = logging.getLogger("spotseeker_server.logger.oauth")
        self.log.setLevel(logging.INFO)
        for handler in self.log.handlers:
            self.log.removeHandler(handler)
        self.log.addHandler(self.handler)

    def test_log_value_2_legged(self):
        with self.settings(
            SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.oauth"
        ):

            consumer_name = "Test consumer"

            key = hashlib.sha1(
                "{0} - {1}".format(random.random(), time.time()).encode(
                    "utf-8"
                )
            ).hexdigest()
            secret = hashlib.sha1(
                "{0} - {1}".format(random.random(), time.time()).encode(
                    "utf-8"
                )
            ).hexdigest()

            create_consumer = Consumer.objects.create(
                name=consumer_name, key=key, secret=secret
            )

            client = oauth1.Client(key, client_secret=secret)
            _, headers, _ = client.sign(
                "http://testserver/api/v1/spot/%s" % self.spot.pk
            )

            response = Client().get(
                self.url, HTTP_AUTHORIZATION=headers["Authorization"]
            )

        with self.settings(
            SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok"
        ):

            self.handler.flush()
            log_message = self.stream.getvalue()

            matches = re.search(
                r'\[.*?\] ([\d]+)\t"(.*?)"\t-\t"GET /api'
                r'/v1/spot/([\d]+)" ([\d]+) ([\d]+)',
                log_message,
            )

            consumer_id = int(matches.group(1))
            consumer_name = matches.group(2)
            spot_id = int(matches.group(3))
            status_code = int(matches.group(4))
            response_size = int(matches.group(5))

            self.assertEquals(
                consumer_id, create_consumer.pk, "Logging correct consumer PK"
            )
            self.assertEquals(
                consumer_name,
                create_consumer.name,
                "Logging correct consumer name",
            )
            self.assertEquals(spot_id, self.spot.pk, "Logging correct uri")
            self.assertEquals(
                status_code,
                response.status_code,
                "Logging correct status_code",
            )
            self.assertEquals(
                response_size,
                len(response.content.decode()),
                "Logging correct content size",
            )

    def test_log_trusted_3_legged(self):
        with self.settings(
            SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.oauth"
        ):
            consumer_name = "Trusted test consumer"

            key = hashlib.sha1(
                "{0} - {1}".format(random.random(), time.time()).encode(
                    "utf-8"
                )
            ).hexdigest()
            secret = hashlib.sha1(
                "{0} - {1}".format(random.random(), time.time()).encode(
                    "utf-8"
                )
            ).hexdigest()

            create_consumer = Consumer.objects.create(
                name=consumer_name, key=key, secret=secret
            )
            trusted_consumer = TrustedOAuthClient.objects.create(
                consumer=create_consumer,
                is_trusted=True,
                bypasses_user_authorization=False,
            )

            client = oauth1.Client(key, client_secret=secret)
            _, headers, _ = client.sign(
                "http://testserver/api/v1/spot/%s" % self.spot.pk
            )

            c = Client()
            response = c.get(
                self.url, HTTP_AUTHORIZATION=headers["Authorization"]
            )
            etag = response["ETag"]

            spot_dict = json.loads(response.content)
            spot_dict["name"] = "Failing to modify oauth"
            spot_dict["location"] = {"latitude": 55, "longitude": -30}

            response = c.put(
                self.url,
                json.dumps(spot_dict),
                content_type="application/json",
                If_Match=etag,
                HTTP_AUTHORIZATION=headers["Authorization"],
                HTTP_X_OAUTH_USER="pmichaud",
            )
            self.assertEquals(
                response.status_code,
                200,
                "Accespts a PUT from a trusted oauth client",
            )

        with self.settings(
            SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok"
        ):

            self.handler.flush()
            log_message = self.stream.getvalue()

            matches = re.search(
                r'\n\[.*?\] ([\d]+)\t"(.*?)"\t(.*?)\t"PUT /api/v1/spo'
                r't/([\d]+)" ([\d]+) ([\d]+)',
                log_message,
                re.MULTILINE,
            )

            consumer_id = int(matches.group(1))
            consumer_name = matches.group(2)
            user_name = matches.group(3)
            spot_id = int(matches.group(4))
            status_code = int(matches.group(5))
            response_size = int(matches.group(6))

            self.assertEquals(
                consumer_id, create_consumer.pk, "Logging correct consumer PK"
            )
            self.assertEquals(
                consumer_name,
                create_consumer.name,
                "Logging correct consumer name",
            )
            self.assertEquals(
                user_name, "pmichaud", "Logging correct oauth username"
            )
            self.assertEquals(spot_id, self.spot.pk, "Logging correct uri")
            self.assertEquals(
                status_code,
                response.status_code,
                "Logging correct status_code",
            )
            self.assertEquals(
                response_size,
                len(response.content.decode()),
                "Logging correct content size",
            )

    def test_invalid(self):
        with self.settings(
            SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.oauth"
        ):

            c = Client()
            response = c.get(self.url)

        with self.settings(
            SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok"
        ):

            self.handler.flush()
            log_message = self.stream.getvalue()

            matches = re.search(
                r'\[.*?\] -\t"-"\t-\t"GET /api/v1/spot'
                r'/([\d]+)" ([\d]+) ([\d]+)',
                log_message,
            )

            spot_id = int(matches.group(1))
            status_code = int(matches.group(2))
            response_size = int(matches.group(3))

            self.assertEquals(spot_id, self.spot.pk, "Logging correct uri")
            self.assertEquals(
                status_code,
                response.status_code,
                "Logging correct status_code",
            )
            self.assertEquals(
                response_size,
                len(response.content),
                "Logging correct content size",
            )

    def tearDown(self):
        self.log.removeHandler(self.handler)
        self.handler.close()

        settings.MIDDLEWARE = self.original_middleware
