# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import secrets
import shutil
import tempfile

from django.test import TestCase
from django.test.utils import override_settings
from django.test.client import Client
from os.path import abspath, dirname, isfile
from spotseeker_server.models import Spot, SpotImage, TrustedOAuthClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from PIL import Image
from oauth_provider.models import Consumer
import random
import hashlib
import time
from oauthlib import oauth1
import simplejson as json
from mock import patch
from spotseeker_server import models

TEST_ROOT = abspath(dirname(__file__))


@override_settings(SPOTSEEKER_AUTH_ADMINS=("pmichaud",))
@override_settings(SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.oauth")
class SpotResourceOAuthImageTest(TestCase):
    #In these tests the oauth signature for the same url could've been reused 
    #However, for every single request a new oauth signature is issued
    #Emulating a situation, where, oauth signatures are time stamped
    def setUp(self):
        self.TEMP_DIR = tempfile.mkdtemp()

        #Setting up oauth
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
        self.trusted_consumer = TrustedOAuthClient.objects.create(
            consumer=create_consumer,
            is_trusted=True,
            bypasses_user_authorization=False,
        )

        self.client = oauth1.Client(key, client_secret=secret)
        

        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            spot_post = Spot.objects.create(
                name="This is to test posting images in the spot resource, with oauth"
            )
            self.spot_post = spot_post

            spot_put = Spot.objects.create(
                name="This is to test puting images in the spot resource, with oauth"
            )
            self.spot_put = spot_put
            self.put_url = "http://testserver/api/v1/spot/{0}".format(self.spot_put.pk)

            # JPEG for PUT test
            jpeg = self.spot_put.spotimage_set.create(
                description="This is the JPEG PUT test",
                image=SimpleUploadedFile(
                    "test_jpeg.jpg",
                    open(
                        "%s/../resources/test_jpeg.jpg" % TEST_ROOT, "rb"
                    ).read(),
                    "image/jpeg",
                ),
            )

            self.jpeg = jpeg
            self.jpeg_url = "%s/image/%s" % (self.put_url, self.jpeg.pk)

            spot_delete = Spot.objects.create(
                name="This is to test deleting images in the spot resource, with oauth"
            )
            self.spot_delete = spot_delete
            self.delete_url = "http://testserver/api/v1/spot/{0}".format(self.spot_delete.pk)

            #GIF for DELETE test
            gif = self.spot_delete.spotimage_set.create(
                description="This is the GIF DELETE test",
                image=SimpleUploadedFile(
                    "test_gif.gif",
                    open(
                        "%s/../resources/test_gif.gif" % TEST_ROOT, "rb"
                    ).read(),
                    "image/gif",
                ),
            )
            self.gif = gif
            self.gif_url = "%s/image/%s" % (self.delete_url, self.gif.pk)
            



    def tearDown(self):
        shutil.rmtree(self.TEMP_DIR)
    
    #POST a PNG image, ensure that the spot has only 1 image and user attributes are correct
    def test_oauth_attributes_post(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            _, headers, _ = self.client.sign(
                "http://testserver/api/v1/spot/%s" % self.spot_post.pk
            )
            c = Client()
            response = c.post(
                "/api/v1/spot/{0}/image".format(self.spot_post.pk),
                {
                    "description": "This is the PNG POST test",
                    "image": SimpleUploadedFile(
                    "test_png.png",
                    open(
                            "%s/../resources/test_png.png" % TEST_ROOT,
                            "rb",
                        ).read(),
                            "image/png",
                        ),
                },
                HTTP_AUTHORIZATION=headers["Authorization"],
                HTTP_X_OAUTH_USER="pmichaud",
            )

        __, headers2, __ = self.client.sign(
                "http://testserver/api/v1/spot/%s" % self.spot_post.pk
            )

        response = c.get("/api/v1/spot/{0}".format(self.spot_post.pk),
        HTTP_AUTHORIZATION=headers2["Authorization"],
        HTTP_X_OAUTH_USER="pmichaud",)

        spot_dict = json.loads(response.content)

        self.assertEquals(len(spot_dict["images"]), 1, "Has 1 image")

        self.assertEquals(
            spot_dict["images"][0]["upload_application"],
            "Test consumer",
            "Image has the proper upload application",
        )
        self.assertEquals(
            spot_dict["images"][0]["upload_user"],
            "pmichaud",
            "Image has the proper upload user",
        )

    #Get a JPEG image (image1), change it via PUT (image2), make sure that PUT request was 200 & image1!=image2
    def test_oauth_attributes_put(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            _, headers, _ = self.client.sign(self.put_url)
            c = Client()
            response = c.get(self.put_url, HTTP_AUTHORIZATION=headers["Authorization"],
            HTTP_X_OAUTH_USER="pmichaud")
            spot_dict_before = json.loads(response.content)

            ____, get_headers, ____ = self.client.sign(self.jpeg_url)
            response = c.get(self.jpeg_url, HTTP_AUTHORIZATION=get_headers["Authorization"],
            HTTP_X_OAUTH_USER="pmichaud")
            etag = response["ETag"]

            new_name = "testing PUT name: {0}".format(random.random())

            __,put_headers,__ = self.client.sign(
                self.jpeg_url
            )
            response = c.put(
                self.jpeg_url,
                files={
                    "description": new_name,
                    "image": SimpleUploadedFile(
                        "test_jpeg2.jpg",
                        open(
                            "%s/../resources/test_jpeg2.jpg" % TEST_ROOT, "rb"
                        ).read(),
                        "image/jpeg",
                    ),
                },
                content_type="multipart/form-data; boundary=--aklsjf--",
                If_Match=etag,
                HTTP_AUTHORIZATION=put_headers["Authorization"],
                HTTP_X_OAUTH_USER="pmichaud",
            )
            self.assertEquals(response.status_code, 200, "PUT was successful")

            ___, get_headers, ___ = self.client.sign(self.put_url)
            response = c.get(self.put_url, HTTP_AUTHORIZATION=get_headers["Authorization"],
            HTTP_X_OAUTH_USER="pmichaud")
            spot_dict_after = json.loads(response.content)
            self.assertNotEquals(spot_dict_before["images"][0], spot_dict_after["images"][0], "Images weren't equal after PUT")

    #Delete a GIF image, confirm that DELETE is succesful, further GET & DELETE return 404, image no longer exists as a file
    def test_oauth_attributes_delete(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            _, headers, _ = self.client.sign(self.gif_url)
            c = Client()
            response = c.get(self.gif_url, HTTP_AUTHORIZATION=headers["Authorization"],HTTP_X_OAUTH_USER="pmichaud")
            etag = response["ETag"]

            __,delete_headers,__ = self.client.sign(self.gif_url)
            response = c.delete(self.gif_url, If_Match=etag, HTTP_AUTHORIZATION=delete_headers["Authorization"], 
            HTTP_X_OAUTH_USER="pmichaud")
            self.assertEquals(response.status_code, 200)

            ___,get_headers,___ = self.client.sign(self.gif_url)
            response = c.get(self.gif_url, HTTP_AUTHORIZATION=get_headers["Authorization"],HTTP_X_OAUTH_USER="pmichaud")
            self.assertEquals(response.status_code, 404)

            ____,delete2_headers,____= self.client.sign(self.gif_url)
            response = c.delete(self.gif_url, If_Match=etag, HTTP_AUTHORIZATION=delete2_headers["Authorization"], 
            HTTP_X_OAUTH_USER="pmichaud")
            self.assertEqual(response.status_code, 404)

            self.assertEqual(isfile(self.gif.image.path), False)

            