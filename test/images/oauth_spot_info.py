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
from os.path import abspath, dirname
from spotseeker_server.models import Spot, SpotImage, TrustedOAuthClient
from django.core.files import File
from django.conf import settings
from PIL import Image
from oauth_provider.models import Consumer
import random
import hashlib
import time
import oauth2
import simplejson as json
from mock import patch
from django.core import cache
from spotseeker_server import models

TEST_ROOT = abspath(dirname(__file__))

@override_settings(SPOTSEEKER_AUTH_ADMINS=('pmichaud',))
class SpotResourceOAuthImageTest(TestCase):
    def setUp(self):
        spot = Spot.objects.create(name="This is to test images in the spot resource, with oauth")
        self.spot = spot

    def test_oauth_attributes(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.oauth'):

                consumer_name = "Test consumer"

                key = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()
                secret = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()

                create_consumer = Consumer.objects.create(name=consumer_name, key=key, secret=secret)
                trusted_consumer = TrustedOAuthClient.objects.create(consumer=create_consumer, is_trusted=True)

                consumer = oauth2.Consumer(key=key, secret=secret)

                req = oauth2.Request.from_consumer_and_token(consumer, None, http_method='POST', http_url="http://testserver/api/v1/spot/{0}/image/".format(self.spot.pk))

                oauth_header = req.to_header()
                c = Client()

                f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
                response = c.post("/api/v1/spot/{0}/image".format(self.spot.pk),
                                  {"description": "oauth image", "image": f},
                                  HTTP_AUTHORIZATION=oauth_header['Authorization'],
                                  HTTP_XOAUTH_USER="pmichaud")

            with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok'):
                response = c.get('/api/v1/spot/{0}'.format(self.spot.pk))

                spot_dict = json.loads(response.content)

                self.assertEquals(len(spot_dict["images"]), 1, "Has 1 image")

                self.assertEquals(spot_dict["images"][0]["upload_application"], "Test consumer", "Image has the proper upload application")
                self.assertEquals(spot_dict["images"][0]["upload_user"], "pmichaud", "Image has the proper upload user")
