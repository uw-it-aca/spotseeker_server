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
from django.test.client import Client, encode_multipart
from django.core.files import File
from spotseeker_server.models import Spot, SpotImage
from os.path import abspath, dirname
import os
import random
import tempfile
import shutil
from django.test.utils import override_settings
from mock import patch
from spotseeker_server import models

TEST_ROOT = abspath(dirname(__file__))


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
@override_settings(SPOTSEEKER_AUTH_ADMINS=('demo_user',))
class SpotImagePUTTest(TestCase):
    """ Tests updating a SpotImage by PUTting to
        /api/v1/spot/<spot id>/image/<image_id>.
    """

    def setUp(self):
        self.TEMP_DIR = tempfile.mkdtemp()
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            spot = Spot.objects.create(
                name="This is to test PUTtingimages",
                capacity=1)
            spot.save()
            self.spot = spot

            self.url = '/api/v1/spot/{0}'.format(self.spot.pk)
            self.url = self.url

            # GIF
            f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
            gif = self.spot.spotimage_set.create(
                description="This is the GIF test",
                image=File(f))
            f.close()

            self.gif = gif
            self.gif_url = "%s/image/%s" % (self.url, self.gif.pk)

            # JPEG
            f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
            jpeg = self.spot.spotimage_set.create(
                description="This is the JPEG test",
                image=File(f))
            f.close()

            self.jpeg = jpeg
            self.jpeg_url = "%s/image/%s" % (self.url, self.jpeg.pk)

            # PNG
            f = open("%s/../resources/test_png.png" % TEST_ROOT)
            png = self.spot.spotimage_set.create(
                description="This is the PNG test",
                image=File(f))
            f.close()

            self.png = png
            self.png_url = "%s/image/%s" % (self.url, self.png.pk)

    def test_bad_url(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            spot = Spot.objects.create(name="This is the wrong spot")

            url = "/api/v1/spot/{0}/image/{1}".format(
                spot.pk,
                self.jpeg.pk)
            response = c.put(url, '{}', content_type="application/json")
            self.assertEquals(response.status_code, 404)

    def test_invalid_url(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            bad_url = "%s/image/aa" % self.url
            response = c.put(bad_url,
                             '{}',
                             content_type="application/json")
            self.assertEquals(response.status_code, 404)

    def test_invalid_id_too_high(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            test_id = self.gif.pk + 10000
            test_url = "%s/image/%s" % (self.url, test_id)
            response = c.put(test_url,
                             '{}',
                             content_type="application/json")
            self.assertEquals(response.status_code, 404)

    def test_valid_same_type_with_etag(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            response = c.get(self.jpeg_url)
            etag = response["etag"]

            f = open("%s/../resources/test_jpeg2.jpg" % TEST_ROOT)
            f2 = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)

            new_jpeg_name = "testing PUT name: {0}".format(random.random())

            response = c.put(self.jpeg_url,
                             files={"description": new_jpeg_name,
                                    "image": f},
                             If_Match=etag)
            f = open("%s/../resources/test_jpeg2.jpg" % TEST_ROOT)
            self.assertEquals(response.status_code, 200)
            self.assertEquals(int(response["content-length"]),
                              len(f.read()))
            self.assertNotEqual(int(response["content-length"]),
                                len(f2.read()))
            self.assertEquals(response["content-type"], "image/jpeg")

    def test_valid_different_image_type_valid_etag(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            response = c.get(self.gif_url)
            etag = response["etag"]

            f = open("%s/../resources/test_png.png" % TEST_ROOT)
            f2 = open("%s/../resources/test_gif.gif" % TEST_ROOT)

            new_name = "testing PUT name: {0}".format(random.random())

            response = c.put(self.gif_url,
                             files={"description": new_name,
                                    "image": f},
                             content_type="multipart/form-data; "
                                          "boundary=--aklsjf--",
                             If_Match=etag)
            self.assertEquals(response.status_code, 200)
            f = open("%s/../resources/test_png.png" % TEST_ROOT)

            # Just to be sure
            response = c.get(self.gif_url)
            self.assertEquals(response["content-type"], "image/png")
            self.assertEquals(int(response["content-length"]),
                              len(f.read()))
            self.assertNotEqual(int(response["content-length"]),
                                len(f2.read()))

    def test_invalid_image_type_valid_etag(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            response = c.get(self.gif_url)
            etag = response["etag"]

            f = open("%s/../resources/test_png.png" % TEST_ROOT)
            f2 = open("%s/../resources/test_gif.gif" % TEST_ROOT)

            new_name = "testing PUT name: {0}".format(random.random())

            c = Client()
            f = open("%s/../resources/fake_jpeg.jpg" % TEST_ROOT)
            response = c.put(self.gif_url,
                             files={"description": "This is a text file",
                                    "image": f},
                             If_Match=etag)
            f.close()
            self.assertEquals(response.status_code, 400)

    # Want this to be one of the first tests to run
    def test_a_valid_image_no_etag(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            # GIF
            f = open("%s/../resources/test_gif2.gif" % TEST_ROOT)
            new_gif_name = "testing PUT name: {0}".format(random.random())
            response = c.put(self.gif_url,
                             files={"description": new_gif_name,
                                    "image": f},
                             content_type="image/gif")
            self.assertEquals(response.status_code, 400)

            updated_img = SpotImage.objects.get(pk=self.gif.pk)
            self.assertEquals(updated_img.image, self.gif.image)

            # JPEG
            f = open("%s/../resources/test_jpeg2.jpg" % TEST_ROOT)
            new_jpeg_name = "testing PUT name: {0}".format(random.random())
            response = c.put(self.gif_url,
                             files={"description": new_jpeg_name,
                                    "image": f},
                             content_type="image/jpeg")
            self.assertEquals(response.status_code, 400)

            updated_img = SpotImage.objects.get(pk=self.jpeg.pk)
            self.assertEquals(updated_img.description,
                              self.jpeg.description)

            # PNG
            f = open("%s/../resources/test_png2.png" % TEST_ROOT)
            new_png_name = "testing PUT name: {0}".format(random.random())
            response = c.put(self.gif_url,
                             files={"description": new_png_name,
                                    "image": f},
                             content_type="image/png")
            self.assertEquals(response.status_code, 400)

            updated_img = SpotImage.objects.get(pk=self.png.pk)
            self.assertEquals(updated_img.description,
                              self.png.description)

            response = c.get(self.gif_url)
            content_length = response["content-length"]
            self.assertNotEqual(os.fstat(f.fileno()).st_size,
                                int(content_length))

            f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
            self.assertEquals(os.fstat(f.fileno()).st_size,
                              int(content_length))

    def tearDown(self):
        shutil.rmtree(self.TEMP_DIR)
