# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import shutil
import tempfile

from django.test import TestCase
from django.test.client import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from spotseeker_server.models import Spot, SpotImage
from os.path import abspath, dirname, isfile
from django.test.utils import override_settings

TEST_ROOT = abspath(dirname(__file__))


@override_settings(SPOTSEEKER_OAUTH_ENABLED=False)
@override_settings(SPOTSEEKER_AUTH_ADMINS=("demo_user",))
class SpotImageDELETETest(TestCase):
    """Tests DELETE of a SpotImage at /api/v1/spot/<spot id>/image/<image id>.
    """

    def setUp(self):
        self.TEMP_DIR = tempfile.mkdtemp()
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            spot = Spot.objects.create(name="This is to test DELETEing images")
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

    def tearDown(self):
        shutil.rmtree(self.TEMP_DIR)

    def test_bad_url(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            bad_url = "%s/image/aa" % self.url
            response = c.delete(bad_url)
            self.assertEquals(response.status_code, 404)

    def test_wrong_spot_id(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            spot = Spot.objects.create(name="This is the wrong spot")

            png = self.spot.spotimage_set.create(
                description="This is another PNG",
                image=SimpleUploadedFile(
                    "test_png.png",
                    open(
                        "%s/../resources/test_png.png" % TEST_ROOT, "rb"
                    ).read(),
                    "image/png",
                ),
            )

            response = c.delete(
                "/api/v1/spot/{0}/image/{1}".format(spot.pk, png.pk)
            )
            self.assertEquals(response.status_code, 404)

    def test_invalid_id_too_high(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()

            # GIF
            test_gif_id = self.gif.pk + 10000
            test_url = "/api/v1/spot/%s/image/%s" % (self.url, test_gif_id)
            response = c.delete(test_url)
            self.assertEquals(response.status_code, 404)

    def test_actual_delete_with_etag(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()

            # GIF
            response = c.get(self.gif_url)
            etag = response["ETag"]

            response = c.delete(self.gif_url, If_Match=etag)

            self.assertEquals(response.status_code, 200)

            response = c.get(self.gif_url)
            self.assertEquals(response.status_code, 404)

            response = c.delete(self.gif_url)
            self.assertEquals(response.status_code, 404)

            self.assertEqual(isfile(self.gif.image.path), False)

            try:
                test_gif = SpotImage.objects.get(pk=self.gif.pk)
            except Exception as e:
                test_gif = None

            self.assertIsNone(test_gif)

            # JPEG
            response = c.get(self.jpeg_url)
            etag = response["ETag"]

            response = c.delete(self.jpeg_url, If_Match=etag)

            self.assertEquals(response.status_code, 200)

            response = c.get(self.jpeg_url)
            self.assertEquals(response.status_code, 404)

            response = c.delete(self.jpeg_url)
            self.assertEquals(response.status_code, 404)

            self.assertEqual(isfile(self.jpeg.image.path), False)

            try:
                test_jpeg = SpotImage.objects.get(pk=self.jpeg.pk)
            except Exception as e:
                test_jpeg = None

            self.assertIsNone(test_jpeg)

            # PNG
            response = c.get(self.png_url)
            etag = response["ETag"]

            response = c.delete(self.png_url, If_Match=etag)

            self.assertEquals(response.status_code, 200)

            response = c.get(self.png_url)
            self.assertEquals(response.status_code, 404)

            response = c.delete(self.png_url)
            self.assertEquals(response.status_code, 404)

            self.assertEqual(isfile(self.png.image.path), False)

            try:
                test_png = SpotImage.objects.get(pk=self.png.pk)
            except Exception as e:
                test_png = None

            self.assertIsNone(test_png)

    def test_actual_delete_no_etag(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()

            # GIF
            response = c.delete(self.gif_url)
            self.assertEquals(response.status_code, 400)

            response = c.get(self.gif_url)
            self.assertEquals(response.status_code, 200)

            # JPEG
            response = c.delete(self.jpeg_url)
            self.assertEquals(response.status_code, 400)

            response = c.get(self.jpeg_url)
            self.assertEquals(response.status_code, 200)

            # PNG
            response = c.delete(self.png_url)
            self.assertEquals(response.status_code, 400)

            response = c.get(self.png_url)
            self.assertEquals(response.status_code, 200)

    def test_actual_delete_expired_etag(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()

            # GIF
            response = c.get(self.gif_url)
            etag = response["ETag"]

            intermediate_img = SpotImage.objects.get(pk=self.gif.pk)
            intermediate_img.name = "This interferes w/ the DELETE"
            intermediate_img.save()

            response = c.delete(self.gif_url, If_Match=etag)
            self.assertEquals(response.status_code, 409)

            response = c.get(self.gif_url)
            self.assertEquals(response.status_code, 200)

            # JPEG
            response = c.get(self.jpeg_url)
            etag = response["ETag"]

            intermediate_img = SpotImage.objects.get(pk=self.jpeg.pk)
            intermediate_img.name = "This interferes w/ the DELETE"
            intermediate_img.save()

            response = c.delete(self.jpeg_url, If_Match=etag)
            self.assertEquals(response.status_code, 409)

            response = c.get(self.jpeg_url)
            self.assertEquals(response.status_code, 200)

            # PNG
            response = c.get(self.png_url)
            etag = response["ETag"]

            intermediate_img = SpotImage.objects.get(pk=self.png.pk)
            intermediate_img.name = "This interferes w/ the DELETE"
            intermediate_img.save()

            response = c.delete(self.png_url, If_Match=etag)
            self.assertEquals(response.status_code, 409)

            response = c.get(self.png_url)
            self.assertEquals(response.status_code, 200)
