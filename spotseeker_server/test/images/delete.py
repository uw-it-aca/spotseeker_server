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
from spotseeker_server.models import Spot, SpotImage
from os.path import abspath, dirname, isfile
from django.test.utils import override_settings
from mock import patch
from django.core import cache
from spotseeker_server import models

TEST_ROOT = abspath(dirname(__file__))


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
@override_settings(SPOTSEEKER_AUTH_ADMINS=('demo_user',))
class SpotImageDELETETest(TestCase):
    """ Tests DELETE of a SpotImage at /api/v1/spot/<spot id>/image/<image id>.
    """
    def setUp(self):
        spot = Spot.objects.create(name="This is to test DELETEing images")
        spot.save()
        self.spot = spot

        self.url = '/api/v1/spot/{0}'.format(self.spot.pk)
        self.url = self.url

        # GIF
        f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
        gif = self.spot.spotimage_set.create(description="This is the GIF test", image=File(f))
        f.close()

        self.gif = gif
        self.gif_url = "%s/image/%s" % (self.url, self.gif.pk)

        # JPEG
        f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
        jpeg = self.spot.spotimage_set.create(description="This is the JPEG test", image=File(f))
        f.close()

        self.jpeg = jpeg
        self.jpeg_url = "%s/image/%s" % (self.url, self.jpeg.pk)

        # PNG
        f = open("%s/../resources/test_png.png" % TEST_ROOT)
        png = self.spot.spotimage_set.create(description="This is the PNG test", image=File(f))
        f.close()

        self.png = png
        self.png_url = "%s/image/%s" % (self.url, self.png.pk)

    def test_bad_url(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            bad_url = "%s/image/aa" % self.url
            response = c.delete(bad_url)
            self.assertEquals(response.status_code, 404, "Rejects an invalid url")

    def test_wrong_spot_id(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            spot = Spot.objects.create(name="This is the wrong spot")

            f = open("%s/../resources/test_png.png" % TEST_ROOT)
            png = self.spot.spotimage_set.create(description="This is another PNG", image=File(f))
            f.close()

            response = c.delete("/api/v1/spot/{0}/image/{1}".format(spot.pk, png.pk))
            self.assertEquals(response.status_code, 404, "Gives a 404 for a spot image that doesn't match the spot")

    def test_invalid_id_too_high(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()

            #GIF
            test_gif_id = self.gif.pk + 10000
            test_url = "/api/v1/spot/%s/image/%s" % (self.url, test_gif_id)
            response = c.delete(test_url)
            self.assertEquals(response.status_code, 404, "Rejects a not-yet existant url")

    def test_actual_delete_with_etag(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()

            #GIF
            response = c.get(self.gif_url)
            etag = response["ETag"]

            response = c.delete(self.gif_url, If_Match=etag)

            self.assertEquals(response.status_code, 200, "Gives a GONE in response to a valid delete")

            response = c.get(self.gif_url)
            self.assertEquals(response.status_code, 404, "Gives a 404 on GET after a delete")

            response = c.delete(self.gif_url)
            self.assertEquals(response.status_code, 404, "Gives a 404 on DELETE after a delete")

            self.assertEqual(isfile(self.gif.image.path), False)

            try:
                test_gif = SpotImage.objects.get(pk=self.gif.pk)
            except Exception as e:
                test_gif = None

            self.assertIsNone(test_gif, "Can't objects.get a deleted SpotImage")

            #JPEG
            response = c.get(self.jpeg_url)
            etag = response["ETag"]

            response = c.delete(self.jpeg_url, If_Match=etag)

            self.assertEquals(response.status_code, 200, "Gives a GONE in response to a valid delete")

            response = c.get(self.jpeg_url)
            self.assertEquals(response.status_code, 404, "Gives a 404 on GET after a delete")

            response = c.delete(self.jpeg_url)
            self.assertEquals(response.status_code, 404, "Gives a 404 on DELETE after a delete")

            self.assertEqual(isfile(self.jpeg.image.path), False)

            try:
                test_jpeg = SpotImage.objects.get(pk=self.jpeg.pk)
            except Exception as e:
                test_jpeg = None

            self.assertIsNone(test_jpeg, "Can't objects.get a deleted SpotImage")

            #PNG
            response = c.get(self.png_url)
            etag = response["ETag"]

            response = c.delete(self.png_url, If_Match=etag)

            self.assertEquals(response.status_code, 200, "Gives a GONE in response to a valid delete")

            response = c.get(self.png_url)
            self.assertEquals(response.status_code, 404, "Gives a 404 on GET after a delete")

            response = c.delete(self.png_url)
            self.assertEquals(response.status_code, 404, "Gives a 404 on DELETE after a delete")

            self.assertEqual(isfile(self.png.image.path), False)

            try:
                test_png = SpotImage.objects.get(pk=self.png.pk)
            except Exception as e:
                test_png = None

            self.assertIsNone(test_png, "Can't objects.get a deleted SpotImage")

    def test_actual_delete_no_etag(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()

            #GIF
            response = c.delete(self.gif_url)
            self.assertEquals(response.status_code, 400, "Deleting w/o an etag is a bad request")

            response = c.get(self.gif_url)
            self.assertEquals(response.status_code, 200, "Resource still exists after DELETE w/o an etag")

            #JPEG
            response = c.delete(self.jpeg_url)
            self.assertEquals(response.status_code, 400, "Deleting w/o an etag is a bad request")

            response = c.get(self.jpeg_url)
            self.assertEquals(response.status_code, 200, "Resource still exists after DELETE w/o an etag")

            #PNG
            response = c.delete(self.png_url)
            self.assertEquals(response.status_code, 400, "Deleting w/o an etag is a bad request")

            response = c.get(self.png_url)
            self.assertEquals(response.status_code, 200, "Resource still exists after DELETE w/o an etag")

    def test_actual_delete_expired_etag(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()

            #GIF
            response = c.get(self.gif_url)
            etag = response["ETag"]

            intermediate_img = SpotImage.objects.get(pk=self.gif.pk)
            intermediate_img.name = "This interferes w/ the DELETE"
            intermediate_img.save()

            response = c.delete(self.gif_url, If_Match=etag)
            self.assertEquals(response.status_code, 409, "Deleting w an outdated etag is a conflict")

            response = c.get(self.gif_url)
            self.assertEquals(response.status_code, 200, "Resource still exists after DELETE w/o an etag")

            #JPEG
            response = c.get(self.jpeg_url)
            etag = response["ETag"]

            intermediate_img = SpotImage.objects.get(pk=self.jpeg.pk)
            intermediate_img.name = "This interferes w/ the DELETE"
            intermediate_img.save()

            response = c.delete(self.jpeg_url, If_Match=etag)
            self.assertEquals(response.status_code, 409, "Deleting w an outdated etag is a conflict")

            response = c.get(self.jpeg_url)
            self.assertEquals(response.status_code, 200, "Resource still exists after DELETE w/o an etag")

            #PNG
            response = c.get(self.png_url)
            etag = response["ETag"]

            intermediate_img = SpotImage.objects.get(pk=self.png.pk)
            intermediate_img.name = "This interferes w/ the DELETE"
            intermediate_img.save()

            response = c.delete(self.png_url, If_Match=etag)
            self.assertEquals(response.status_code, 409, "Deleting w an outdated etag is a conflict")

            response = c.get(self.png_url)
            self.assertEquals(response.status_code, 200, "Resource still exists after DELETE w/o an etag")
