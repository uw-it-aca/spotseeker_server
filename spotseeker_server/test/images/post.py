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

from django.conf import settings
from django.core import cache
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from mock import patch
from os.path import abspath, dirname
from spotseeker_server import models
from spotseeker_server.models import Spot
import json
import random
import shutil
import tempfile

TEST_ROOT = abspath(dirname(__file__))


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
@override_settings(SPOTSEEKER_AUTH_ADMINS=('demo_user',))
class SpotImagePOSTTest(TestCase):
    """ Tests POSTing to /api/v1/spot/<spot id>/image.
    """

    def setUp(self):
        self.TEMP_DIR = tempfile.mkdtemp()
        spot = Spot.objects.create(name="This is to test adding images")
        spot.save()
        self.spot = spot

        self.url = '/api/v1/spot/{0}/image'.format(self.spot.pk)
        self.url = self.url

    def test_jpeg(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
                response = c.post(self.url, {"description": "This is a jpeg", "image": f})
                f.close()

                self.assertEquals(response.status_code, 201, "Gives a Created response to posting a jpeg")

    def test_gif(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
                response = c.post(self.url, {"description": "This is a gif", "image": f})
                f.close()

                self.assertEquals(response.status_code, 201, "Gives a Created response to posting a gif")

    def test_png(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/test_png.png" % TEST_ROOT)
                response = c.post(self.url, {"description": "This is a png", "image": f})
                f.close()

                self.assertEquals(response.status_code, 201, "Gives a Created response to posting a png")

    def test_display_index(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
                response = c.post(self.url, {"description": "This is a jpeg", "display_index": 1,"image": f})
                f.close()

                self.assertEquals(response.status_code, 201, "Gives a Created response to posting a jpeg")

                response = c.get(self.spot.rest_url())
                spot_dict = json.loads(response.content)
                self.assertEquals(spot_dict['images'].__len__(), 1, "Spot has only 1 SpotImage")
                self.assertEquals(spot_dict['images'][0]['display_index'], 1, "Image created with a display index of 1 has a display index of 1")

    def test_no_display_index(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
                response = c.post(self.url, {"description": "This is a jpeg", "image": f})
                f.close()
                self.assertEquals(response.status_code, 201, "Gives a Created response to posting a jpeg")
                f = open("%s/../resources/test_png.png" % TEST_ROOT)
                response = c.post(self.url, {"description": "This is a png", "image": f})
                f.close()
                self.assertEquals(response.status_code, 201, "Gives a Created response to posting a png")

                response = c.get(self.spot.rest_url())
                spot_dict = json.loads(response.content)
                self.assertEquals(spot_dict['images'].__len__(), 2, "Spot has 2 SpotImages")
                self.assertEquals(spot_dict['images'][0]['display_index'], 0, "First returned spot has a display index of 0")
                self.assertEquals(spot_dict['images'][0]['description'], "This is a jpeg", "First returned spot is the jpeg")
                self.assertEquals(spot_dict['images'][1]['display_index'], 1, "Second returned spot has a display index of 1")
                self.assertEquals(spot_dict['images'][1]['description'], "This is a png", "First returned spot is the png")

    def test_invalid_image_type(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/test_bmp.bmp" % TEST_ROOT)
                response = c.post(self.url, {"description": "This is a bmp file - invalid format", "image": f})
                f.close()

                self.assertEquals(response.status_code, 400, "Gives a Bad Request in response to a non-accepted image format")

    def test_invalid_file(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/fake_jpeg.jpg" % TEST_ROOT)
                response = c.post(self.url, {"description": "This is really a text file", "image": f})
                f.close()

                self.assertEquals(response.status_code, 400, "Gives a Bad Request in response to a non-image")

    def test_no_file(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                response = c.post(self.url, {"description": "This is really a text file"})

                self.assertEquals(response.status_code, 400, "Gives a Bad Request in response to no image")

    def test_wrong_field(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
                response = c.post(self.url, {"description": "This is a gif", "not_image": f})
                f.close()

                self.assertEquals(response.status_code, 400, "Gives an error for a file uploaded with the wrong field name")

    def test_wrong_url(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            with self.settings(MEDIA_ROOT=self.TEMP_DIR):
                c = Client()
                f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
                response = c.post('/api/v1/spot/{0}/image'.format(self.spot.pk + 1), {"description": "This is a gif", "image": f})
                f.close()

                self.assertEquals(response.status_code, 404, "Gives an error trying to upload a photo to a non-existant spot")

    def tearDown(self):
        shutil.rmtree(self.TEMP_DIR)
