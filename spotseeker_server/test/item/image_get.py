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

from cStringIO import StringIO
from django.conf import settings
from django.core import cache
from django.core.files import File
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


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
class ItemImageGETTest(TestCase):

    dummy_cache_setting = {
        'default': { 
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

    def setUp(self):
        item = Item.objects.create(name="This is to test getting images")
        item.save()
        self.item = item

        f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
        gif = ItemImage.objects.create(
            description="This is the GIF test",
            item=item, image=File(f))
        f.close()

        self.gif = gif

        f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
        jpeg = ItemImage.objects.create(
            description="This is the JPEG test",
            item=item, image=File(f))
        f.close()

        self.jpeg = jpeg

        f = open("%s/../resources/test_png.png" % TEST_ROOT)
        png = ItemImage.objects.create(
            description="This is the PNG test",
            item=item,
            image=File(f))
        f.close()

        self.png = png

        self.url = '/api/v1/item/{0}/image'.format(self.item.pk)
        self.url = self.url

    @override_settings(CACHES=dummy_cache_setting)
    def test_bad_url(self):
        c = Client()
        item = Item.objects.create(name="This is the wrong item")

        response = c.get("/api/v1/item/{0}/image/{1}".
                            format(item.pk, self.jpeg.pk))
        self.assertEquals(response.status_code, 404)

    @override_settings(CACHES=dummy_cache_setting)

    def test_jpeg(self):
        c = Client()
        response = c.get("{0}/{1}".format(self.url, self.jpeg.pk))
        data = StringIO(response.content)
        im = Image.open(data)
        self.assertEquals(response["Content-type"], "image/jpeg")

        orig = Image.open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)

        self.assertEquals(im.size[0], orig.size[0])
        self.assertEquals(im.size[1], orig.size[1])
        self.assertEquals(im.format, 'JPEG')

    @override_settings(CACHES=dummy_cache_setting)
    def test_gif(self):
        c = Client()
        response = c.get("{0}/{1}".format(self.url, self.gif.pk))
        data = StringIO(response.content)
        im = Image.open(data)
        self.assertEquals(response["Content-type"], "image/gif")

        orig = Image.open("%s/../resources/test_gif.gif" % TEST_ROOT)

        self.assertEquals(im.size[0], orig.size[0])
        self.assertEquals(im.size[1], orig.size[1])
        self.assertEquals(im.format, 'GIF')

    @override_settings(CACHES=dummy_cache_setting)
    def test_png(self):
        c = Client()
        response = c.get("{0}/{1}".format(self.url, self.png.pk))
        data = StringIO(response.content)
        im = Image.open(data)
        self.assertEquals(response["Content-type"], "image/png")

        orig = Image.open("%s/../resources/test_png.png" % TEST_ROOT)

        self.assertEquals(im.size[0], orig.size[0])
        self.assertEquals(im.size[1], orig.size[1])
        self.assertEquals(im.format, 'PNG')
