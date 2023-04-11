# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.conf import settings
from django.test.client import Client, encode_multipart
from django.core.files.uploadedfile import SimpleUploadedFile
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


@override_settings(SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok")
@override_settings(SPOTSEEKER_AUTH_ADMINS=("demo_user",))
class SpotImagePUTTest(TestCase):
    """Tests updating a SpotImage by PUTting to
    /api/v1/spot/<spot id>/image/<image_id>.
    """

    def setUp(self):
        self.TEMP_DIR = tempfile.mkdtemp()
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            spot = Spot.objects.create(
                name="This is to test PUTtingimages", capacity=1
            )
            spot.save()
            self.spot = spot

            self.url = "/api/v1/spot/{0}".format(self.spot.pk)
            self.url = self.url

            # GIF
            gif = self.spot.spotimage_set.create(
                description="This is the GIF test",
                image=SimpleUploadedFile(
                    "test_gif.gif",
                    open(
                        "%s/../resources/test_gif.gif" % TEST_ROOT, "rb"
                    ).read(),
                    "image/gif",
                ),
            )

            self.gif = gif
            self.gif_url = "%s/image/%s" % (self.url, self.gif.pk)

            # JPEG
            jpeg = self.spot.spotimage_set.create(
                description="This is the JPEG test",
                image=SimpleUploadedFile(
                    "test_jpeg.jpg",
                    open(
                        "%s/../resources/test_jpeg.jpg" % TEST_ROOT, "rb"
                    ).read(),
                    "image/jpeg",
                ),
            )

            self.jpeg = jpeg
            self.jpeg_url = "%s/image/%s" % (self.url, self.jpeg.pk)

            # PNG
            png = self.spot.spotimage_set.create(
                description="This is the PNG test",
                image=SimpleUploadedFile(
                    "test_png.png",
                    open(
                        "%s/../resources/test_png.png" % TEST_ROOT, "rb"
                    ).read(),
                    "image/png",
                ),
            )

            self.png = png
            self.png_url = "%s/image/%s" % (self.url, self.png.pk)

    def test_bad_url(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            spot = Spot.objects.create(name="This is the wrong spot")

            url = "/api/v1/spot/{0}/image/{1}".format(spot.pk, self.jpeg.pk)
            response = c.put(url, "{}", content_type="application/json")
            self.assertEquals(response.status_code, 404)

    def test_invalid_url(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            bad_url = "%s/image/aa" % self.url
            response = c.put(bad_url, "{}", content_type="application/json")
            self.assertEquals(response.status_code, 404)

    def test_invalid_id_too_high(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            test_id = self.gif.pk + 10000
            test_url = "%s/image/%s" % (self.url, test_id)
            response = c.put(test_url, "{}", content_type="application/json")
            self.assertEquals(response.status_code, 404)

    def test_valid_same_type_with_etag(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            response = c.get(self.jpeg_url)
            try:
                etag = unicode(response["etag"])
            except NameError:
                etag = response["etag"]
            new_jpeg_name = "testing PUT name: {0}".format(random.random())

            response = c.put(
                self.jpeg_url,
                files={
                    "description": new_jpeg_name,
                    "image": SimpleUploadedFile(
                        "test_jpeg2.jpg",
                        open(
                            "%s/../resources/test_jpeg2.jpg" % TEST_ROOT, "rb"
                        ).read(),
                        "image/jpeg",
                    ),
                },
                If_Match=etag,
            )
            f = open("%s/../resources/test_jpeg2.jpg" % TEST_ROOT, "rb")
            f2 = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT, "rb")
            self.assertEquals(response.status_code, 200)
            self.assertEquals(int(response["content-length"]), len(f.read()))
            self.assertNotEqual(
                int(response["content-length"]), len(f2.read())
            )
            self.assertEquals(response["content-type"], "image/jpeg")

    def test_valid_different_image_type_valid_etag(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            response = c.get(self.gif_url)
            try:
                etag = unicode(response["etag"])
            except NameError:
                etag = response["etag"]
            new_name = "testing PUT name: {0}".format(random.random())

            response = c.put(
                self.gif_url,
                files={
                    "description": new_name,
                    "image": SimpleUploadedFile(
                        new_name,
                        open(
                            "%s/../resources/test_png.png" % TEST_ROOT, "rb"
                        ).read(),
                        "image/png",
                    ),
                },
                content_type="multipart/form-data; boundary=--aklsjf--",
                If_Match=etag,
            )
            self.assertEquals(response.status_code, 200)
            f = open("%s/../resources/test_png.png" % TEST_ROOT, "rb")
            f2 = open("%s/../resources/test_gif.gif" % TEST_ROOT, "rb")

            # Just to be sure
            response = c.get(self.gif_url)
            self.assertEquals(response["content-type"], "image/png")
            self.assertEquals(int(response["content-length"]), len(f.read()))
            self.assertNotEqual(
                int(response["content-length"]), len(f2.read())
            )

    def test_invalid_image_type_valid_etag(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            response = c.get(self.gif_url)
            etag = response["etag"]

            f = open("%s/../resources/test_png.png" % TEST_ROOT, "rb")
            f2 = open("%s/../resources/test_gif.gif" % TEST_ROOT, "rb")

            new_name = "testing PUT name: {0}".format(random.random())

            c = Client()
            f = open("%s/../resources/fake_jpeg.jpg" % TEST_ROOT, "rb")
            response = c.put(
                self.gif_url,
                files={"description": "This is a text file", "image": f},
                If_Match=etag,
            )
            f.close()
            self.assertEquals(response.status_code, 400)

    # Want this to be one of the first tests to run
    def test_a_valid_image_no_etag(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            # GIF
            f = open("%s/../resources/test_gif2.gif" % TEST_ROOT, "rb")
            new_gif_name = "testing PUT name: {0}".format(random.random())
            response = c.put(
                self.gif_url,
                files={"description": new_gif_name, "image": f},
                content_type="image/gif",
            )
            self.assertEquals(response.status_code, 400)

            updated_img = SpotImage.objects.get(pk=self.gif.pk)
            self.assertEquals(updated_img.image, self.gif.image)

            # JPEG
            f = open("%s/../resources/test_jpeg2.jpg" % TEST_ROOT, "rb")
            new_jpeg_name = "testing PUT name: {0}".format(random.random())
            response = c.put(
                self.gif_url,
                files={"description": new_jpeg_name, "image": f},
                content_type="image/jpeg",
            )
            self.assertEquals(response.status_code, 400)

            updated_img = SpotImage.objects.get(pk=self.jpeg.pk)
            self.assertEquals(updated_img.description, self.jpeg.description)

            # PNG
            f = open("%s/../resources/test_png2.png" % TEST_ROOT, "rb")
            new_png_name = "testing PUT name: {0}".format(random.random())
            response = c.put(
                self.gif_url,
                files={"description": new_png_name, "image": f},
                content_type="image/png",
            )
            self.assertEquals(response.status_code, 400)

            updated_img = SpotImage.objects.get(pk=self.png.pk)
            self.assertEquals(updated_img.description, self.png.description)

            response = c.get(self.gif_url)
            content_length = response["content-length"]
            self.assertNotEqual(
                os.fstat(f.fileno()).st_size, int(content_length)
            )

            f = open("%s/../resources/test_gif.gif" % TEST_ROOT, "rb")
            self.assertEquals(
                os.fstat(f.fileno()).st_size, int(content_length)
            )

    def tearDown(self):
        shutil.rmtree(self.TEMP_DIR)
