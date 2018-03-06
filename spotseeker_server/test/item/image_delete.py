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
from django.test.client import Client
from django.core.files import File
from spotseeker_server.models import Item, ItemImage, Spot
from os.path import abspath, dirname, isfile
from django.test.utils import override_settings
from django.utils.unittest import skipUnless
from mock import patch
from django.core import cache
from spotseeker_server import models

TEST_ROOT = abspath(dirname(__file__))


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
@override_settings(SPOTSEEKER_AUTH_ADMINS=('demo_user',))
class ItemImageDELETETest(TestCase):
    """ Tests DELETE of a ItemImage at /api/v1/item/<item id>/image/<image id>.
    """
    def setUp(self):
        spot = Spot.objects.create(
            name="This is a spot for testing DELETEing images")
        spot.save()
        item = Item.objects.create(
            name="This is to test DELETEing images",
            spot=spot    
        )
        item.save()
        self.item = item

        self.url = '/api/v1/item/{0}'.format(self.item.pk)
        self.url = self.url

        # GIF
        f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
        gif = self.item.itemimage_set.create(
            description="This is the GIF test",
            image=File(f))
        f.close()

        self.gif = gif
        self.gif_url = "%s/image/%s" % (self.url, self.gif.pk)

        # JPEG
        f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
        jpeg = self.item.itemimage_set.create(
            description="This is the JPEG test",
            image=File(f))
        f.close()

        self.jpeg = jpeg
        self.jpeg_url = "%s/image/%s" % (self.url, self.jpeg.pk)

        # PNG
        f = open("%s/../resources/test_png.png" % TEST_ROOT)
        png = self.item.itemimage_set.create(
            description="This is the PNG test",
            image=File(f))
        f.close()

        self.png = png
        self.png_url = "%s/image/%s" % (self.url, self.png.pk)

    def test_bad_url(self):
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            bad_url = "%s/image/aa" % self.url
            response = c.delete(bad_url)
            self.assertEquals(response.status_code, 404)

    def test_wrong_item_id(self):
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            item = Item.objects.create(name="This is the wrong item")

            f = open("%s/../resources/test_png.png" % TEST_ROOT)
            png = self.item.itemimage_set.create(
                description="This is another PNG", image=File(f))
            f.close()

            response = \
                c.delete("/api/v1/item/{0}/image/{1}".format(item.pk, png.pk))
            self.assertEquals(response.status_code, 404)

    def test_invalid_id_too_high(self):
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()

            # GIF
            test_gif_id = self.gif.pk + 10000
            test_url = "/api/v1/item/%s/image/%s" % (self.url, test_gif_id)
            response = c.delete(test_url)
            self.assertEquals(response.status_code, 404)

    def test_actual_delete_no_etag(self):
        dummy_cache = cache.get_cache(
            'django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
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
