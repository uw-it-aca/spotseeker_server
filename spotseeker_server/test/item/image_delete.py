# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import shutil
import tempfile

from django.test import TestCase
from django.test.client import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from spotseeker_server.models import Item, ItemImage, Spot
from os.path import abspath, dirname
from django.test.utils import override_settings

TEST_ROOT = abspath(dirname(__file__))


@override_settings(SPOTSEEKER_OAUTH_ENABLED=False)
@override_settings(SPOTSEEKER_AUTH_ADMINS=("demo_user",))
class ItemImageDELETETest(TestCase):
    """Tests DELETE of a ItemImage at /api/v1/item/<item id>/image/<image id>.
    """

    dummy_cache_setting = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }

    def setUp(self):
        self.TEMP_DIR = tempfile.mkdtemp()
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            spot = Spot.objects.create(
                name="This is a spot for testing DELETEing images"
            )
            spot.save()
            item = Item.objects.create(
                name="This is to test DELETEing images", spot=spot
            )
            item.save()
            self.item = item

            self.url = "/api/v1/item/{0}".format(self.item.pk)
            self.url = self.url

            # GIF
            gif = self.item.itemimage_set.create(
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
            jpeg = self.item.itemimage_set.create(
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
            png = self.item.itemimage_set.create(
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

    @override_settings(CACHES=dummy_cache_setting)
    def test_bad_url(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            bad_url = "%s/image/aa" % self.url
            response = c.delete(bad_url)
            self.assertEquals(response.status_code, 404)

    @override_settings(CACHES=dummy_cache_setting)
    def test_wrong_item_id(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            item = Item.objects.create(name="This is the wrong item")

            png = self.item.itemimage_set.create(
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
                "/api/v1/item/{0}/image/{1}".format(item.pk, png.pk)
            )
            self.assertEquals(response.status_code, 404)

    @override_settings(CACHES=dummy_cache_setting)
    def test_invalid_id_too_high(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()

            # GIF
            test_gif_id = self.gif.pk + 10000
            test_url = "/api/v1/item/%s/image/%s" % (self.url, test_gif_id)
            response = c.delete(test_url)
            self.assertEquals(response.status_code, 404)

    @override_settings(CACHES=dummy_cache_setting)
    def test_actual_delete_no_etag(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()

            # GIF
            response = c.delete(self.gif_url)

            self.assertEquals(response.status_code, 200)

            response = c.get(self.gif_url)
            self.assertEquals(response.status_code, 404)

            # JPEG
            response = c.delete(self.jpeg_url)
            self.assertEquals(response.status_code, 200)

            response = c.get(self.jpeg_url)
            self.assertEquals(response.status_code, 404)

            # PNG
            response = c.delete(self.png_url)
            self.assertEquals(response.status_code, 200)

            response = c.get(self.png_url)
            self.assertEquals(response.status_code, 404)
