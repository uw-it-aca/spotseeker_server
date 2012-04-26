from django.utils import unittest
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

TEST_ROOT = abspath(dirname(__file__))

class SpotResourceOAuthImageTest(unittest.TestCase):
    def setUp(self):
        spot = Spot.objects.create( name = "This is to test images in the spot resource, with oauth" )
        self.spot = spot

    def test_oauth_attributes(self):
        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.oauth';

        consumer_name = "Test consumer"

        key = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()
        secret = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()

        create_consumer = Consumer.objects.create(name=consumer_name, key=key, secret=secret)
        trusted_consumer = TrustedOAuthClient.objects.create(consumer = create_consumer, is_trusted = True)

        consumer = oauth2.Consumer(key=key, secret=secret)

        req = oauth2.Request.from_consumer_and_token(consumer, None, http_method='POST', http_url="http://testserver/api/v1/spot/{0}/image/".format(self.spot.pk))

        oauth_header = req.to_header()
        c = Client()

        f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
        response = c.post("/api/v1/spot/{0}/image".format(self.spot.pk),
                          {"description": "oauth image", "image": f},
                          HTTP_AUTHORIZATION=oauth_header['Authorization'],
                          HTTP_XOAUTH_USER="pmichaud")

        settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok';

        response = c.get('/api/v1/spot/{0}'.format(self.spot.pk))

        spot_dict = json.loads(response.content)

        self.assertEquals(len(spot_dict["images"]), 1, "Has 1 image")

        self.assertEquals(spot_dict["images"][0]["upload_application"], "Test consumer", "Image has the proper upload application")
        self.assertEquals(spot_dict["images"][0]["upload_user"], "pmichaud", "Image has the proper upload user")


