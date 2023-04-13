# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from spotseeker_server.models import Spot, TrustedOAuthClient, Client
import simplejson as json
import hashlib
import time
import random
from oauthlib import oauth1
from django.test.utils import override_settings
from unittest.mock import patch, MagicMock
from spotseeker_server import models
from spotseeker_server.require_auth import get_auth_module, get_auth_method
from spotseeker_server.auth import all_ok, oauth, fake_oauth
from django.core.exceptions import ImproperlyConfigured


@override_settings(SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.oauth")
class SpotAuthOAuth(TestCase):
    def setUp(self):
        spot = Spot.objects.create(
            name="This is for testing the oauth module", capacity=10
        )
        self.spot = spot
        self.url = "/api/v1/spot/%s" % self.spot.pk

    def test_get_no_oauth(self):
        c = self.client
        response = c.get(self.url)
        self.assertEquals(
            response.status_code, 401, "No access to GET w/o oauth"
        )

    def test_valid_oauth(self):
        consumer_name = "Test consumer"

        key = hashlib.sha1(
            "{0} - {1}".format(random.random(), time.time()).encode("utf-8")
        ).hexdigest()
        secret = hashlib.sha1(
            "{0} - {1}".format(random.random(), time.time()).encode("utf-8")
        ).hexdigest()

        create_consumer = Client.objects.create(
            name=consumer_name, key=key, secret=secret
        )

        client = oauth1.Client(key, client_secret=secret)
        _, headers, _ = client.sign("http://testserver" + self.url)

        c = self.client
        response = c.get(self.url, HTTP_AUTHORIZATION=headers["Authorization"])

        self.assertEquals(
            response.status_code,
            200,
            "Got a 200 w/ a proper oauth client connection",
        )

        spot_dict = json.loads(response.content)

        self.assertEquals(
            spot_dict["id"], self.spot.pk, "Got the right spot back from oauth"
        )

    def test_invalid_oauth(self):
        client = oauth1.Client(
            "This is a fake key", client_secret="This is a fake secret"
        )
        _, headers, _ = client.sign("http://testserver" + self.url)

        c = self.client
        response = c.get(self.url, HTTP_AUTHORIZATION=headers["Authorization"])

        self.assertEquals(
            response.status_code,
            401,
            "Got a 401 w/ an invented oauth client id",
        )

    @override_settings(
        SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms.sp"
        "ot.DefaultSpotForm"
    )
    @override_settings(
        SPOTSEEKER_SPOTEXTENDEDINFO_FORM="spotseeker_server.default_forms.sp"
        "ot.DefaultSpotExtendedInfoForm"
    )
    def test_put_no_oauth(self):
        c = self.client

        response = c.get(self.url)

        etag = self.spot.etag

        spot_dict = self.spot.json_data_structure()
        spot_dict["name"] = "Failing to modify oauth"

        response = c.put(
            self.url,
            json.dumps(spot_dict),
            content_type="application/json",
            If_Match=etag,
        )
        self.assertEquals(
            response.status_code, 401, "Rejects a PUT w/o oauth info"
        )

    @override_settings(
        SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms.sp"
        "ot.DefaultSpotForm"
    )
    @override_settings(
        SPOTSEEKER_SPOTEXTENDEDINFO_FORM="spotseeker_server.default_forms.sp"
        "ot.DefaultSpotExtendedInfoForm"
    )
    def test_put_untrusted_oauth(self):
        consumer_name = "Untrusted test consumer"

        key = hashlib.sha1(
            "{0} - {1}".format(random.random(), time.time()).encode("utf-8")
        ).hexdigest()
        secret = hashlib.sha1(
            "{0} - {1}".format(random.random(), time.time()).encode("utf-8")
        ).hexdigest()

        create_consumer = Client.objects.create(
            name=consumer_name, key=key, secret=secret
        )

        client = oauth1.Client(key, client_secret=secret)
        _, headers, _ = client.sign("http://testserver" + self.url)

        c = self.client
        response = c.get(self.url, HTTP_AUTHORIZATION=headers["Authorization"])
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
        )
        self.assertEquals(
            response.status_code,
            401,
            "Rejects a PUT from a non-trusted oauth client",
        )

    @override_settings(
        SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms.sp"
        "ot.DefaultSpotForm"
    )
    @override_settings(
        SPOTSEEKER_SPOTEXTENDEDINFO_FORM="spotseeker_server.default_forms.sp"
        "ot.DefaultSpotExtendedInfoForm"
    )
    def test_put_untrusted_oauth_with_user_header(self):
        consumer_name = "Untrusted test consumer"

        key = hashlib.sha1(
            "{0} - {1}".format(random.random(), time.time()).encode("utf-8")
        ).hexdigest()
        secret = hashlib.sha1(
            "{0} - {1}".format(random.random(), time.time()).encode("utf-8")
        ).hexdigest()

        create_consumer = Client.objects.create(
            name=consumer_name, key=key, secret=secret
        )

        client = oauth1.Client(key, client_secret=secret)
        _, headers, _ = client.sign("http://testserver" + self.url)

        c = self.client
        response = c.get(self.url, HTTP_AUTHORIZATION=headers["Authorization"])
        etag = response["ETag"]

        spot_dict = json.loads(response.content)
        spot_dict["name"] = "Failing to modify oauth"

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
            401,
            "Rejects a PUT from a non-trusted oauth client",
        )

    @override_settings(
        SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms.sp"
        "ot.DefaultSpotForm"
    )
    @override_settings(
        SPOTSEEKER_SPOTEXTENDEDINFO_FORM="spotseeker_server.default_forms.sp"
        "ot.DefaultSpotExtendedInfoForm"
    )
    @override_settings(SPOTSEEKER_AUTH_ADMINS=("pmichaud",))
    def test_put_trusted_client(self):
        consumer_name = "Trusted test consumer"

        key = hashlib.sha1(
            "{0} - {1}".format(random.random(), time.time()).encode("utf-8")
        ).hexdigest()
        secret = hashlib.sha1(
            "{0} - {1}".format(random.random(), time.time()).encode("utf-8")
        ).hexdigest()

        create_consumer = Client.objects.create(
            name=consumer_name, key=key, secret=secret
        )
        trusted_consumer = TrustedOAuthClient.objects.create(
            consumer=create_consumer,
            is_trusted=True,
            bypasses_user_authorization=False,
        )

        client = oauth1.Client(key, client_secret=secret)
        _, headers, _ = client.sign("http://testserver" + self.url)

        c = self.client
        response = c.get(self.url, HTTP_AUTHORIZATION=headers["Authorization"])
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
            "Accepts a PUT from a trusted oauth client",
        )

    @override_settings(
        SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms.sp"
        "ot.DefaultSpotForm"
    )
    @override_settings(
        SPOTSEEKER_SPOTEXTENDEDINFO_FORM="spotseeker_server.default_forms.sp"
        "ot.DefaultSpotExtendedInfoForm"
    )
    def test_put_trusted_client_no_user(self):
        consumer_name = "Trusted test consumer"

        key = hashlib.sha1(
            "{0} - {1}".format(random.random(), time.time()).encode("utf-8")
        ).hexdigest()
        secret = hashlib.sha1(
            "{0} - {1}".format(random.random(), time.time()).encode("utf-8")
        ).hexdigest()

        create_consumer = Client.objects.create(
            name=consumer_name, key=key, secret=secret
        )
        trusted_consumer = TrustedOAuthClient.objects.create(
            consumer=create_consumer,
            is_trusted=True,
            bypasses_user_authorization=False,
        )

        client = oauth1.Client(key, client_secret=secret)
        _, headers, _ = client.sign("http://testserver" + self.url)

        c = self.client
        response = c.get(self.url, HTTP_AUTHORIZATION=headers["Authorization"])
        etag = response["ETag"]

        spot_dict = json.loads(response.content)
        spot_dict["name"] = "Failing to modify oauth"

        response = c.put(
            self.url,
            json.dumps(spot_dict),
            content_type="application/json",
            If_Match=etag,
            HTTP_AUTHORIZATION=headers["Authorization"],
        )
        self.assertEquals(
            response.status_code,
            401,
            "Rejects a PUT from a trusted oauth client w/o a given user",
        )

    def test_create_trusted_client(self):
        """Tests to be sure the create_consumer
        command can create trusted clients.
        """
        consumer_name = "This is for testing create_consumer"

        call_command(
            "create_consumer",
            consumer_name=consumer_name,
            trusted="yes",
            silent=True,
        )

        consumer = Client.objects.get(name=consumer_name)

        client = TrustedOAuthClient.objects.get(consumer=consumer)

        self.assertIsInstance(client, TrustedOAuthClient)

    @override_settings()
    def test_get_auth_module(self):
        del settings.SPOTSEEKER_AUTH_MODULE
        self.assertEqual(all_ok, get_auth_module())

        with override_settings(SPOTSEEKER_AUTH_MODULE=''
                               'spotseeker_server.auth.all_ok'):
            self.assertEqual(all_ok, get_auth_module())

        with override_settings(SPOTSEEKER_AUTH_MODULE=''
                               'spotseeker_server.auth.oauth'):
            self.assertEqual(oauth, get_auth_module())

        with override_settings(SPOTSEEKER_AUTH_MODULE=''
                               'spotseeker_server.auth.fake_oauth'):
            self.assertEqual(fake_oauth, get_auth_module())

    @override_settings()
    def test_get_auth_method(self):
        with override_settings(SPOTSEEKER_AUTH_MODULE=''
                               'spotseeker_server.auth.all_ok'):
            self.assertEqual(None,
                             get_auth_method('authenticate_application')())

        with override_settings(SPOTSEEKER_AUTH_MODULE=''
                               'spotseeker_server.auth.fake_oauth'):
            self.assertEqual(None,
                             get_auth_method('authenticate_application')())

        with override_settings(SPOTSEEKER_AUTH_MODULE=''
                               'spotseeker_server.auth.oauth'):
            auth_method = get_auth_method('authenticate_application')
            response = auth_method('bad arg0', 'bad arg1')
            self.assertEqual(401, response.status_code)

        self.assertRaises(ImproperlyConfigured, get_auth_method, 'fake')
