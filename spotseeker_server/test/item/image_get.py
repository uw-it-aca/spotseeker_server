# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import shutil
import tempfile

try:
    from cStringIO import StringIO as IOStream
except ModuleNotFoundError:
    from io import BytesIO as IOStream

from django.conf import settings
from django.core import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from mock import patch
from os.path import abspath, dirname
from PIL import Image
from spotseeker_server.models import Item, ItemImage
from spotseeker_server import models
import random

TEST_ROOT = abspath(dirname(__file__))


@override_settings(SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok")
class ItemImageGETTest(TestCase):

    dummy_cache_setting = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }

    def setUp(self):
        self.TEMP_DIR = tempfile.mkdtemp()
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            item = Item.objects.create(name="This is to test getting images")
            item.save()
            self.item = item

            gif = ItemImage.objects.create(
                description="This is the GIF test",
                item=item,
                image=SimpleUploadedFile(
                    "test_gif.gif",
                    open(
                        "%s/../resources/test_gif.gif" % TEST_ROOT, "rb"
                    ).read(),
                    "image/gif",
                ),
            )
            self.gif = gif

            jpeg = ItemImage.objects.create(
                description="This is the JPEG test",
                item=item,
                image=SimpleUploadedFile(
                    "test_jpeg.jpg",
                    open(
                        "%s/../resources/test_jpeg.jpg" % TEST_ROOT, "rb"
                    ).read(),
                    "image/jpeg",
                ),
            )
            self.jpeg = jpeg

            png = ItemImage.objects.create(
                description="This is the PNG test",
                item=item,
                image=SimpleUploadedFile(
                    "test_png.png",
                    open(
                        "%s/../resources/test_png.png" % TEST_ROOT, "rb"
                    ).read(),
                    "image/png",
                ),
            )
            self.png = png

            self.url = "/api/v1/item/{0}/image".format(self.item.pk)
            self.url = self.url

    def tearDown(self):
        shutil.rmtree(self.TEMP_DIR)

    @override_settings(CACHES=dummy_cache_setting)
    def test_bad_url(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            item = Item.objects.create(name="This is the wrong item")

            response = c.get(
                "/api/v1/item/{0}/image/{1}".format(item.pk, self.jpeg.pk)
            )
            self.assertEquals(response.status_code, 404)

    @override_settings(CACHES=dummy_cache_setting)
    def test_jpeg(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            response = c.get("{0}/{1}".format(self.url, self.jpeg.pk))
            data = IOStream(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/jpeg")

            orig = Image.open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)

            self.assertEquals(im.size[0], orig.size[0])
            self.assertEquals(im.size[1], orig.size[1])
            self.assertEquals(im.format, "JPEG")

    @override_settings(CACHES=dummy_cache_setting)
    def test_gif(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            response = c.get("{0}/{1}".format(self.url, self.gif.pk))
            data = IOStream(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/gif")

            orig = Image.open("%s/../resources/test_gif.gif" % TEST_ROOT)

            self.assertEquals(im.size[0], orig.size[0])
            self.assertEquals(im.size[1], orig.size[1])
            self.assertEquals(im.format, "GIF")

    @override_settings(CACHES=dummy_cache_setting)
    def test_png(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            response = c.get("{0}/{1}".format(self.url, self.png.pk))
            data = IOStream(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/png")

            orig = Image.open("%s/../resources/test_png.png" % TEST_ROOT)

            self.assertEquals(im.size[0], orig.size[0])
            self.assertEquals(im.size[1], orig.size[1])
            self.assertEquals(im.format, "PNG")
