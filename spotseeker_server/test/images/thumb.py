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
from django.core.files import File
from django.test.client import Client
from spotseeker_server.models import Spot, SpotImage
from cStringIO import StringIO
from PIL import Image
from os.path import abspath, dirname
from django.test.utils import override_settings
from mock import patch
from django.core import cache
from spotseeker_server import models

TEST_ROOT = abspath(dirname(__file__))


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
@override_settings(SPOTSEEKER_AUTH_ADMINS=('demo_user',))
class ImageThumbTest(TestCase):

    def setUp(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            spot = Spot.objects.create(name="This is to test thumbnailing images")
            spot.save()
            self.spot = spot

            self.url = '/api/v1/spot/{0}/image'.format(self.spot.pk)
            self.url = self.url

    def test_jpeg_thumbs(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
            response = c.post(self.url, {"description": "This is a jpeg", "image": f})
            f.close()

            new_base_location = response["Location"]

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 100, 100))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/jpeg", "Content type of same size thumbnail is jpeg")
            self.assertEquals(im.size[0], 100, "Width on same size jpeg thumbnail is 100")
            self.assertEquals(im.size[1], 100, "Height on same size jpeg thumbnail is 100")
            self.assertEquals(im.format, 'JPEG', "Actual type of same size thumbnail is still a jpeg")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 1, 100))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/jpeg", "Content type of narrow thumbnail is jpeg")
            self.assertEquals(im.size[0], 1, "Width on narrow jpeg thumbnail is 1")
            self.assertEquals(im.size[1], 100, "Height on narrow jpeg thumbnail is 100")
            self.assertEquals(im.format, 'JPEG', "Actual type of narrow thumbnail is still a jpeg")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 100, 1))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/jpeg", "Content type of short thumbnail is jpeg")
            self.assertEquals(im.size[0], 100, "Width on short jpeg thumbnail is 100")
            self.assertEquals(im.size[1], 1, "Height on short jpeg thumbnail is 1")
            self.assertEquals(im.format, 'JPEG', "Actual type of short thumbnail is still a jpeg")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 1, 1))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/jpeg", "Content type of 1-pixel thumbnail is jpeg")
            self.assertEquals(im.size[0], 1, "Width on 1-pixel jpeg thumbnail is 1")
            self.assertEquals(im.size[1], 1, "Height on 1-pixel jpeg thumbnail is 1")
            self.assertEquals(im.format, 'JPEG', "Actual type of 1-pixel thumbnail is still a jpeg")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 200, 200))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/jpeg", "Content type of 200x200 'thumbnail' is jpeg")
            self.assertEquals(im.size[0], 200, "Width on 200x200 jpeg 'thumbnail' is 1")
            self.assertEquals(im.size[1], 200, "Height on 200x200 jpeg 'thumbnail' is 1")
            self.assertEquals(im.format, 'JPEG', "Actual type of 200x200 jpeg 'thumbnail' is still a jpeg")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 100, 0))
            self.assertEquals(response.status_code, 400, "400 for no height, jpeg")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 0, 100))
            self.assertEquals(response.status_code, 400, "400 for no width, jpeg")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 0, 0))
            self.assertEquals(response.status_code, 400, "400 for no width or height, jpeg")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 100, -100))
            self.assertEquals(response.status_code, 400, "400 for negative height, jpeg")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, -100, 100))
            self.assertEquals(response.status_code, 400, "400 for negative width, jpeg")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, "a", 100))
            self.assertEquals(response.status_code, 400, "400 for invalid width, jpeg")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 100, "a"))
            self.assertEquals(response.status_code, 400, "400 for invalid height, jpeg")

    def test_png_thumbs(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            f = open("%s/../resources/test_png.png" % TEST_ROOT)
            response = c.post(self.url, {"description": "This is a png", "image": f})
            f.close()

            new_base_location = response["Location"]

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 100, 100))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/png", "Content type of same size thumbnail is png")
            self.assertEquals(im.size[0], 100, "Width on same size png thumbnail is 100")
            self.assertEquals(im.size[1], 100, "Height on same size png thumbnail is 100")
            self.assertEquals(im.format, 'PNG', "Actual type of same size thumbnail is still a png")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 1, 100))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/png", "Content type of narrow thumbnail is png")
            self.assertEquals(im.size[0], 1, "Width on narrow png thumbnail is 1")
            self.assertEquals(im.size[1], 100, "Height on narrow png thumbnail is 100")
            self.assertEquals(im.format, 'PNG', "Actual type of narrow thumbnail is still a png")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 100, 1))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/png", "Content type of short thumbnail is png")
            self.assertEquals(im.size[0], 100, "Width on short png thumbnail is 100")
            self.assertEquals(im.size[1], 1, "Height on short png thumbnail is 1")
            self.assertEquals(im.format, 'PNG', "Actual type of short thumbnail is still a png")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 1, 1))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/png", "Content type of 1-pixel thumbnail is png")
            self.assertEquals(im.size[0], 1, "Width on 1-pixel png thumbnail is 1")
            self.assertEquals(im.size[1], 1, "Height on 1-pixel png thumbnail is 1")
            self.assertEquals(im.format, 'PNG', "Actual type of 1-pixel thumbnail is still a png")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 200, 200))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/png", "Content type of 200x200 'thumbnail' is png")
            self.assertEquals(im.size[0], 200, "Width on 200x200 png 'thumbnail' is 1")
            self.assertEquals(im.size[1], 200, "Height on 200x200 png 'thumbnail' is 1")
            self.assertEquals(im.format, 'PNG', "Actual type of 200x200 png 'thumbnail' is still a png")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 100, 0))
            self.assertEquals(response.status_code, 400, "400 for no height, png")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 0, 100))
            self.assertEquals(response.status_code, 400, "400 for no width, png")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 0, 0))
            self.assertEquals(response.status_code, 400, "400 for no width or height, png")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 100, -100))
            self.assertEquals(response.status_code, 400, "400 for negative height, png")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, -100, 100))
            self.assertEquals(response.status_code, 400, "400 for negative width, png")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, "a", 100))
            self.assertEquals(response.status_code, 400, "400 for invalid width, png")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 100, "a"))
            self.assertEquals(response.status_code, 400, "400 for invalid height, png")

    def test_gif_thumbs(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
            response = c.post(self.url, {"description": "This is a gif", "image": f})
            f.close()

            new_base_location = response["Location"]

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 100, 100))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/gif", "Content type of same size thumbnail is gif")
            self.assertEquals(im.size[0], 100, "Width on same size gif thumbnail is 100")
            self.assertEquals(im.size[1], 100, "Height on same size gif thumbnail is 100")
            self.assertEquals(im.format, 'GIF', "Actual type of same size thumbnail is still a gif")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 1, 100))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/gif", "Content type of narrow thumbnail is gif")
            self.assertEquals(im.size[0], 1, "Width on narrow gif thumbnail is 1")
            self.assertEquals(im.size[1], 100, "Height on narrow gif thumbnail is 100")
            self.assertEquals(im.format, 'GIF', "Actual type of narrow thumbnail is still a gif")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 100, 1))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/gif", "Content type of short thumbnail is gif")
            self.assertEquals(im.size[0], 100, "Width on short gif thumbnail is 100")
            self.assertEquals(im.size[1], 1, "Height on short gif thumbnail is 1")
            self.assertEquals(im.format, 'GIF', "Actual type of short thumbnail is still a gif")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 1, 1))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/gif", "Content type of 1-pixel thumbnail is gif")
            self.assertEquals(im.size[0], 1, "Width on 1-pixel gif thumbnail is 1")
            self.assertEquals(im.size[1], 1, "Height on 1-pixel gif thumbnail is 1")
            self.assertEquals(im.format, 'GIF', "Actual type of 1-pixel thumbnail is still a gif")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 200, 200))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/gif", "Content type of 200x200 'thumbnail' is gif")
            self.assertEquals(im.size[0], 200, "Width on 200x200 gif 'thumbnail' is 1")
            self.assertEquals(im.size[1], 200, "Height on 200x200 gif 'thumbnail' is 1")
            self.assertEquals(im.format, 'GIF', "Actual type of 200x200 gif 'thumbnail' is still a gif")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 100, 0))
            self.assertEquals(response.status_code, 400, "400 for no height, gif")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 0, 100))
            self.assertEquals(response.status_code, 400, "400 for no width, gif")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 0, 0))
            self.assertEquals(response.status_code, 400, "400 for no width or height, gif")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 100, -100))
            self.assertEquals(response.status_code, 400, "400 for negative height, gif")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, -100, 100))
            self.assertEquals(response.status_code, 400, "400 for negative width, gif")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, "a", 100))
            self.assertEquals(response.status_code, 400, "400 for invalid width, gif")

            response = c.get("{0}/thumb/{1}x{2}".format(new_base_location, 100, "a"))
            self.assertEquals(response.status_code, 400, "400 for invalid height, gif")

    def test_invalid_url(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            bad_spot = Spot.objects.create(name="This is the wrong spot")

            spot = Spot.objects.create(name="This is to test getting images")

            f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
            gif = SpotImage.objects.create(description="This is the GIF test", spot=spot, image=File(f))
            f.close()

            url = "/api/v1/spot/{0}/image/{1}/thumb/10x10".format(bad_spot.pk, gif.pk)
            response = c.get(url)
            self.assertEquals(response.status_code, 404, "Give a 404 for a spot id that doesn't match the image's")

    def test_constrain_jpg(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            img_path = "%s/../resources/test_jpeg2.jpg" % TEST_ROOT
            f = open(img_path)
            response = c.post(self.url, {"description": "This is a jpg", "image": f})
            orig_im = Image.open(img_path)
            f.close()

            new_base_location = response["Location"]

            # constrain width to 50
            response = c.get("{0}/thumb/constrain/width:{1}".format(new_base_location, 50))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/jpeg", "Content type of same size thumbnail is jpg")
            self.assertEquals(im.size[0], 50, "Width on same size jpg thumbnail is 50")
            orig_ratio = orig_im.size[1] / orig_im.size[0]
            ratio = im.size[1] / im.size[0]
            self.assertEquals(ratio, orig_ratio, "Ratio on constrained jpg thumbnail is the same")
            self.assertEquals(im.format, 'JPEG', "Actual type of same size thumbnail is still a jpg")

            # constrain height to 50
            response = c.get("{0}/thumb/constrain/height:{1}".format(new_base_location, 50))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/jpeg", "Content type of same size thumbnail is jpg")
            self.assertEquals(im.size[1], 50, "Height on same size jpg thumbnail is 50")
            orig_ratio = orig_im.size[1] / orig_im.size[0]
            ratio = im.size[1] / im.size[0]
            self.assertEquals(ratio, orig_ratio, "Ratio on constrained jpg thumbnail is the same")
            self.assertEquals(im.format, 'JPEG', "Actual type of same size thumbnail is still a jpg")

            # constrain width to 75, height to 50
            response = c.get("{0}/thumb/constrain/width:{1},height:{2}".format(new_base_location, 75, 50))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/jpeg", "Content type of same size thumbnail is jpg")
            self.assertEquals(im.size[1], 50, "Height on same size jpg thumbnail is 50")
            orig_ratio = orig_im.size[1] / orig_im.size[0]
            ratio = im.size[1] / im.size[0]
            self.assertEquals(ratio, orig_ratio, "Ratio on constrained jpg thumbnail is the same")
            self.assertEquals(im.format, 'JPEG', "Actual type of same size thumbnail is still a jpg")

            # constrain height to 75, width to 50
            response = c.get("{0}/thumb/constrain/height:{1},width:{2}".format(new_base_location, 75, 50))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/jpeg", "Content type of same size thumbnail is jpg")
            self.assertEquals(im.size[1], 75, "Height on same size jpg thumbnail is 50")
            orig_ratio = orig_im.size[1] / orig_im.size[0]
            ratio = im.size[1] / im.size[0]
            self.assertEquals(ratio, orig_ratio, "Ratio on constrained jpg thumbnail is the same")
            self.assertEquals(im.format, 'JPEG', "Actual type of same size thumbnail is still a jpg")

    def test_constrain_png(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            img_path = "%s/../resources/test_png2.png" % TEST_ROOT
            f = open(img_path)
            response = c.post(self.url, {"description": "This is a png", "image": f})
            orig_im = Image.open(img_path)
            f.close()

            new_base_location = response["Location"]

            # constrain width to 50
            response = c.get("{0}/thumb/constrain/width:{1}".format(new_base_location, 50))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/png", "Content type of same size thumbnail is png")
            self.assertEquals(im.size[0], 50, "Width on same size png thumbnail is 50")
            orig_ratio = orig_im.size[1] / orig_im.size[0]
            ratio = im.size[1] / im.size[0]
            self.assertEquals(ratio, orig_ratio, "Ratio on constrained png thumbnail is the same")
            self.assertEquals(im.format, 'PNG', "Actual type of same size thumbnail is still a png")

            # constrain height to 50
            response = c.get("{0}/thumb/constrain/height:{1}".format(new_base_location, 50))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/png", "Content type of same size thumbnail is png")
            self.assertEquals(im.size[1], 50, "Height on same size png thumbnail is 50")
            orig_ratio = orig_im.size[1] / orig_im.size[0]
            ratio = im.size[1] / im.size[0]
            self.assertEquals(ratio, orig_ratio, "Ratio on constrained png thumbnail is the same")
            self.assertEquals(im.format, 'PNG', "Actual type of same size thumbnail is still a png")

            # constrain width to 75, height to 50
            response = c.get("{0}/thumb/constrain/width:{1},height:{2}".format(new_base_location, 75, 50))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/png", "Content type of same size thumbnail is png")
            self.assertEquals(im.size[1], 50, "Height on same size png thumbnail is 50")
            orig_ratio = orig_im.size[1] / orig_im.size[0]
            ratio = im.size[1] / im.size[0]
            self.assertEquals(ratio, orig_ratio, "Ratio on constrained png thumbnail is the same")
            self.assertEquals(im.format, 'PNG', "Actual type of same size thumbnail is still a png")

            # constrain height to 75, width to 50
            response = c.get("{0}/thumb/constrain/height:{1},width:{2}".format(new_base_location, 75, 50))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/png", "Content type of same size thumbnail is png")
            self.assertEquals(im.size[1], 75, "Height on same size png thumbnail is 50")
            orig_ratio = orig_im.size[1] / orig_im.size[0]
            ratio = im.size[1] / im.size[0]
            self.assertEquals(ratio, orig_ratio, "Ratio on constrained png thumbnail is the same")
            self.assertEquals(im.format, 'PNG', "Actual type of same size thumbnail is still a png")

    def test_constrain_gif(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            c = Client()
            img_path = "%s/../resources/test_gif2.gif" % TEST_ROOT
            f = open(img_path)
            response = c.post(self.url, {"description": "This is a gif", "image": f})
            orig_im = Image.open(img_path)
            f.close()

            new_base_location = response["Location"]

            # constrain width to 50
            response = c.get("{0}/thumb/constrain/width:{1}".format(new_base_location, 50))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/gif", "Content type of same size thumbnail is gif")
            self.assertEquals(im.size[0], 50, "Width on same size gif thumbnail is 50")
            orig_ratio = orig_im.size[1] / orig_im.size[0]
            ratio = im.size[1] / im.size[0]
            self.assertEquals(ratio, orig_ratio, "Ratio on constrained gif thumbnail is the same")
            self.assertEquals(im.format, 'GIF', "Actual type of same size thumbnail is still a gif")

            # constrain height to 50
            response = c.get("{0}/thumb/constrain/height:{1}".format(new_base_location, 50))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/gif", "Content type of same size thumbnail is gif")
            self.assertEquals(im.size[1], 50, "Height on same size gif thumbnail is 50")
            orig_ratio = orig_im.size[1] / orig_im.size[0]
            ratio = im.size[1] / im.size[0]
            self.assertEquals(ratio, orig_ratio, "Ratio on constrained gif thumbnail is the same")
            self.assertEquals(im.format, 'GIF', "Actual type of same size thumbnail is still a gif")

            # constrain width to 75, height to 50
            response = c.get("{0}/thumb/constrain/width:{1},height:{2}".format(new_base_location, 75, 50))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/gif", "Content type of same size thumbnail is gif")
            self.assertEquals(im.size[1], 50, "Height on same size gif thumbnail is 50")
            orig_ratio = orig_im.size[1] / orig_im.size[0]
            ratio = im.size[1] / im.size[0]
            self.assertEquals(ratio, orig_ratio, "Ratio on constrained gif thumbnail is the same")
            self.assertEquals(im.format, 'GIF', "Actual type of same size thumbnail is still a gif")

            # constrain height to 75, width to 50
            response = c.get("{0}/thumb/constrain/height:{1},width:{2}".format(new_base_location, 75, 50))
            data = StringIO(response.content)
            im = Image.open(data)
            self.assertEquals(response["Content-type"], "image/gif", "Content type of same size thumbnail is gif")
            self.assertEquals(im.size[1], 75, "Height on same size gif thumbnail is 50")
            orig_ratio = orig_im.size[1] / orig_im.size[0]
            ratio = im.size[1] / im.size[0]
            self.assertEquals(ratio, orig_ratio, "Ratio on constrained gif thumbnail is the same")
            self.assertEquals(im.format, 'GIF', "Actual type of same size thumbnail is still a gif")
