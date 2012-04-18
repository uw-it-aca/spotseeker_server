from django.utils import unittest
from django.conf import settings
from django.test.client import Client
from django.core.files import File
from spotseeker_server.models import Spot, SpotImage
from os.path import abspath, dirname
import random

TEST_ROOT = abspath(dirname(__file__))

class SpotImagePUTTest(unittest.TestCase):
    settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok';
    def setUp(self):
        spot = Spot.objects.create( name = "This is to test PUTtingimages", capacity=1 )
        spot.save()
        self.spot = spot

        self.url = '/api/v1/spot/{0}'.format(self.spot.pk)
        self.url = self.url

        # GIF
        f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
        gif = self.spot.spotimage_set.create( description = "This is the GIF test", image = File(f) )
        f.close()

        self.gif = gif
        self.gif_url = "%s/image/%s" % (self.url, self.gif.pk)

        # JPEG
        f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
        jpeg = self.spot.spotimage_set.create( description = "This is the JPEG test", image = File(f) )
        f.close()

        self.jpeg = jpeg
        self.jpeg_url = "%s/image/%s" % (self.url, self.jpeg.pk)

        # PNG
        f = open("%s/../resources/test_png.png" % TEST_ROOT)
        png = self.spot.spotimage_set.create( description = "This is the PNG test", image = File(f) )
        f.close()

        self.png = png
        self.png_url = "%s/image/%s" % (self.url, self.png.pk)


    def test_invalid_url(self):
        c = Client()
        bad_url = "%s/image/aa" % self.url
        response = c.put(bad_url, '{}', content_type="application/json")
        self.assertEquals(response.status_code, 404, "Rejects a non-numeric url")


    def test_invalid_id_too_high(self):
        c = Client()
        test_id = self.gif.pk + 10000
        test_url = "%s/image/%s" % (self.url, test_id)
        response = c.put(test_url, '{}', content_type="application/json")
        self.assertEquals(response.status_code, 404, "Rejects an id that doesn't exist yet (no PUT to create)")


    def test_valid_image_no_etag(self):
        c = Client()
        #GIF
        #TODO: these actually need to try putting a different img, not the same one
        f = open("%s/../resources/test_gif2.gif" % TEST_ROOT)
        new_gif_name = "testing PUT name: {0}".format(random.random())
        response = c.put(self.gif_url, { "description": new_gif_name, "image": f })
        self.assertEquals(response.status_code, 409, "Conflict w/o an etag")

        updated_img = SpotImage.objects.get(pk=self.gif.pk)
        self.assertEquals(updated_img.image, self.gif.image, "No etag - same image")

        #JPEG
        f = open("%s/../resources/test_jpeg2.jpg" % TEST_ROOT)
        new_jpeg_name = "testing PUT name: {0}".format(random.random())
        response = c.put(self.gif_url, { "description": new_jpeg_name, "image": f })
        self.assertEquals(response.status_code, 409, "Conflict w/o an etag")

        updated_img = SpotImage.objects.get(pk=self.jpeg.pk)
        self.assertEquals(updated_img.image, self.jpeg.name, "No etag - same image")

        #PNG
        f = open("%s/../resources/test_png2.jpg" % TEST_ROOT)
        new_png_name = "testing PUT name: {0}".format(random.random())
        response = c.put(self.gif_url, { "description": new_png_name, "image": f })
        self.assertEquals(response.status_code, 409, "Conflict w/o an etag")

        updated_img = SpotImage.objects.get(pk=self.png.pk)
        self.assertEquals(updated_img.image, self.png.name, "No etag - same image")

