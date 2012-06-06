from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot
import random
from os.path import abspath, dirname
import tempfile
import shutil

TEST_ROOT = abspath(dirname(__file__))


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
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
            response = c.post(self.url, {"description": "This is a jpeg", "image": f})
            f.close()

            self.assertEquals(response.status_code, 201, "Gives a Created response to posting a jpeg")

    def test_gif(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
            response = c.post(self.url, {"description": "This is a gif", "image": f})
            f.close()

            self.assertEquals(response.status_code, 201, "Gives a Created response to posting a gif")

    def test_png(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            f = open("%s/../resources/test_png.png" % TEST_ROOT)
            response = c.post(self.url, {"description": "This is a png", "image": f})
            f.close()

            self.assertEquals(response.status_code, 201, "Gives a Created response to posting a png")

    def test_invalid_image_type(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            f = open("%s/../resources/test_bmp.bmp" % TEST_ROOT)
            response = c.post(self.url, {"description": "This is a bmp file - invalid format", "image": f})
            f.close()

            self.assertEquals(response.status_code, 400, "Gives a Bad Request in response to a non-accepted image format")

    def test_invalid_file(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            f = open("%s/../resources/fake_jpeg.jpg" % TEST_ROOT)
            response = c.post(self.url, {"description": "This is really a text file", "image": f})
            f.close()

            self.assertEquals(response.status_code, 400, "Gives a Bad Request in response to a non-image")

    def test_no_file(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            response = c.post(self.url, {"description": "This is really a text file"})

            self.assertEquals(response.status_code, 400, "Gives a Bad Request in response to no image")

    def test_wrong_field(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
            response = c.post(self.url, {"description": "This is a gif", "not_image": f})
            f.close()

            self.assertEquals(response.status_code, 400, "Gives an error for a file uploaded with the wrong field name")

    def test_wrong_url(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
            response = c.post('/api/v1/spot/{0}/image'.format(self.spot.pk + 1), {"description": "This is a gif", "image": f})
            f.close()

            self.assertEquals(response.status_code, 404, "Gives an error trying to upload a photo to a non-existant spot")

    def tearDown(self):
        shutil.rmtree(self.TEMP_DIR)
