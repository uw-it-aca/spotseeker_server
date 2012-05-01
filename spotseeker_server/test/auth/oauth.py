from django.utils import unittest
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot, TrustedOAuthClient
import simplejson as json
import hashlib
import time
import random
from oauth_provider.models import Consumer
import oauth2


class SpotAuthOAuth(unittest.TestCase):
    def setUp(self):
        spot = Spot.objects.create(name="This is for testing the oauth module", capacity=10)
        self.spot = spot
        self.url = "/api/v1/spot/%s" % self.spot.pk

    def test_get_no_oauth(self):
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.oauth';
        c = Client()
        response = c.get(self.url)
        self.assertEquals(response.status_code, 401, "No access to GET w/o oauth")
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok';

    def test_valid_oauth(self):
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.oauth';
        consumer_name = "Test consumer"

        key = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()
        secret = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()

        create_consumer = Consumer.objects.create(name=consumer_name, key=key, secret=secret)

        consumer = oauth2.Consumer(key=key, secret=secret)

        req = oauth2.Request.from_consumer_and_token(consumer, None, http_method='GET', http_url="http://testserver/api/v1/spot/%s" % self.spot.pk)

        oauth_header = req.to_header()

        c = Client()
        response = c.get(self.url, HTTP_AUTHORIZATION=oauth_header['Authorization'])

        self.assertEquals(response.status_code, 200, "Got a 200 w/ a proper oauth client connection")

        spot_dict = json.loads(response.content)

        self.assertEquals(spot_dict['id'], self.spot.pk, "Got the right spot back from oauth")
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok';

    def test_invalid_oauth(self):
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.oauth';

        consumer = oauth2.Consumer(key="This is a fake key", secret="This is a fake secret")

        req = oauth2.Request.from_consumer_and_token(consumer, None, http_method='GET', http_url="http://testserver/api/v1/spot/%s" % self.spot.pk)

        oauth_header = req.to_header()

        c = Client()
        response = c.get(self.url, HTTP_AUTHORIZATION=oauth_header['Authorization'])

        self.assertEquals(response.status_code, 401, "Got a 401 w/ an invented oauth client id")
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok';

    def test_put_no_oauth(self):
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.oauth';
        c = Client()

        response = c.get(self.url)

        etag = self.spot.etag

        spot_dict = self.spot.json_data_structure()
        spot_dict['name'] = "Failing to modify oauth"

        response = c.put(self.url, json.dumps(spot_dict), content_type="application/json", If_Match=etag)
        self.assertEquals(response.status_code, 401, "Rejects a PUT w/o oauth info")
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok';

    def test_put_untrusted_oauth(self):
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.oauth';
        consumer_name = "Untrusted test consumer"

        key = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()
        secret = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()

        create_consumer = Consumer.objects.create(name=consumer_name, key=key, secret=secret)

        consumer = oauth2.Consumer(key=key, secret=secret)

        req = oauth2.Request.from_consumer_and_token(consumer, None, http_method='GET', http_url="http://testserver/api/v1/spot/%s" % self.spot.pk)

        oauth_header = req.to_header()
        c = Client()

        response = c.get(self.url, HTTP_AUTHORIZATION=oauth_header['Authorization'])
        etag = response["ETag"]

        spot_dict = json.loads(response.content)
        spot_dict['name'] = "Failing to modify oauth"

        response = c.put(self.url, json.dumps(spot_dict), content_type="application/json", If_Match=etag, HTTP_AUTHORIZATION=oauth_header['Authorization'])
        self.assertEquals(response.status_code, 401, "Rejects a PUT from a non-trusted oauth client")
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok';

    def test_put_untrusted_oauth_with_user_header(self):
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.oauth';
        consumer_name = "Untrusted test consumer"

        key = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()
        secret = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()

        create_consumer = Consumer.objects.create(name=consumer_name, key=key, secret=secret)

        consumer = oauth2.Consumer(key=key, secret=secret)

        req = oauth2.Request.from_consumer_and_token(consumer, None, http_method='GET', http_url="http://testserver/api/v1/spot/%s" % self.spot.pk)

        oauth_header = req.to_header()
        c = Client()

        response = c.get(self.url, HTTP_AUTHORIZATION=oauth_header['Authorization'])
        etag = response["ETag"]

        spot_dict = json.loads(response.content)
        spot_dict['name'] = "Failing to modify oauth"

        response = c.put(self.url, json.dumps(spot_dict), content_type="application/json", If_Match=etag, HTTP_AUTHORIZATION=oauth_header['Authorization'], HTTP_XOAUTH_USER="pmichaud")
        self.assertEquals(response.status_code, 401, "Rejects a PUT from a non-trusted oauth client")
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok';

    def test_put_trusted_client(self):
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.oauth';
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

        response = c.put(self.url, json.dumps(spot_dict), content_type="application/json", If_Match=etag, HTTP_AUTHORIZATION=oauth_header['Authorization'], HTTP_XOAUTH_USER="pmichaud")
        self.assertEquals(response.status_code, 200, "Accespts a PUT from a trusted oauth client")
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok';

    def test_put_trusted_client_no_user(self):
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.oauth';
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

        response = c.put(self.url, json.dumps(spot_dict), content_type="application/json", If_Match=etag, HTTP_AUTHORIZATION=oauth_header['Authorization'])
        self.assertEquals(response.status_code, 401, "Rejects a PUT from a trusted oauth client w/o a given user")
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok';
