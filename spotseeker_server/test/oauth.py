# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.test.utils import override_settings
from django.core.management import call_command
from spotseeker_server.models import Spot, TrustedOAuthClient, Client
import simplejson as json
from datetime import timedelta
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application


@override_settings(
    SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms.spot.DefaultSpotForm"
)
@override_settings(
    SPOTSEEKER_SPOTEXTENDEDINFO_FORM="spotseeker_server.default_forms.spot."
                                     "DefaultSpotExtendedInfoForm"
)
@override_settings(SPOTSEEKER_OAUTH_ENABLED=True)
class SpotAuthOAuth(TestCase):
    def setUp(self):
        spot = Spot.objects.create(
            name="This is for testing the oauth module", capacity=10
        )
        self.spot = spot
        self.url = "/api/v1/spot/%s" % self.spot.pk

    def tearDown(self) -> None:
        AccessToken.objects.all().delete()
        Application.objects.all().delete()
        Client.objects.all().delete()
        Spot.objects.all().delete()

        return super().tearDown()

    def _create_auth_header(self, token: str) -> str:
        return "Bearer " + token

    def _create_token(self, client: Client, expiry: int = 300,
                      scope: str = 'read write') -> AccessToken:
        app = Application.objects.create(
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
            name="Test app",
            user=client,
        )

        token = AccessToken.objects.create(
            user=client,
            scope=scope,
            expires=timezone.now() + timedelta(seconds=expiry),
            token="testtoken",
            application=app,
        )

        return token

    def test_get_no_oauth(self):
        c = self.client
        response = c.get(self.url)
        self.assertEquals(
            response.status_code, 401, "No access to GET w/o oauth"
        )

    def test_valid_oauth(self):
        consumer_name = "Test consumer"

        auth_client = Client.objects.create(
            username=consumer_name, name=consumer_name,
            client_id="fake_id", client_secret="fake_secret"
        )
        auth_client.get_client_credential()
        auth_client.save()

        token = self._create_auth_header(
            self._create_token(auth_client).token
        )

        c = self.client

        response = c.get(self.url, HTTP_AUTHORIZATION=token)

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
        consumer_name = "Test consumer"

        auth_client = Client.objects.create(
            username=consumer_name, name=consumer_name,
            client_id="fake_id", client_secret="fake_secret"
        )
        auth_client.get_client_credential()
        auth_client.save()

        token = self._create_auth_header(
            self._create_token(auth_client).token
        )

        c = self.client
        response = c.get(self.url, HTTP_AUTHORIZATION=token + "BAD")

        self.assertEquals(
            response.status_code,
            401,
            "Got a 401 w/ an invented oauth client id",
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

    def test_put_expired_oauth(self):
        consumer_name = "Expired consumer"

        unauth_client = Client.objects.create(
            username=consumer_name, name=consumer_name,
            client_id="fake_id", client_secret="fake_secret"
        )
        unauth_client.get_client_credential()
        unauth_client.save()

        token = self._create_auth_header(
            self._create_token(unauth_client, -1).token
        )

        c = self.client
        response = c.get(self.url, HTTP_AUTHORIZATION=token)

        self.assertEquals(
            response.status_code,
            401,
            "Rejects a GET from an expired oauth client",
        )

    def test_put_read_only_oauth(self):
        consumer_name = "Read-only consumer"

        unauth_client = Client.objects.create(
            username=consumer_name, name=consumer_name,
            client_id="fake_id", client_secret="fake_secret"
        )
        unauth_client.get_client_credential()
        unauth_client.save()

        token = self._create_auth_header(
            self._create_token(unauth_client, scope='read').token
        )

        c = self.client
        response = c.get(self.url, HTTP_AUTHORIZATION=token)

        self.assertEquals(
            response.status_code,
            200,
            "Accepts a GET from a read-only oauth client",
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
            HTTP_AUTHORIZATION=token,
        )

        self.assertEquals(
            response.status_code,
            403,
            "Rejects a PUT from a non-trusted oauth client",
        )

    def test_create_trusted_client(self):
        """Tests to be sure the create_consumer
        command can create trusted clients.
        """
        consumer_name = "This is for testing create_consumer"

        call_command(
            "create_consumer",
            consumer_name=consumer_name,
            trusted=True,
            silent=True,
        )

        consumer = Client.objects.get(name=consumer_name)

        client = TrustedOAuthClient.objects.get(consumer=consumer)

        self.assertIsInstance(client, TrustedOAuthClient)
