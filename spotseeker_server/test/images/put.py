from django.utils import unittest
from django.test.client import Client
from django.core.files import File
from spotseeker_server.models import Spot, SpotImage
from os.path import abspath, dirname

TEST_ROOT = abspath(dirname(__file__))

class SpotImagePUTTest(unittest.TestCase):
    def setUp(self):
        spot = Spot.objects.create( name = "This is to test PUTtingimages" )
        spot.save()
        self.spot = spot

        self.url = '/api/v1/spot/{0}'.format(self.spot.pk)
        self.url = self.url

        # GIF
        f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
        gif = self.spot.spotimage_set.create( description = "This is the GIF test", image = File(f) )
        gif.save()
        f.close()

        self.gif = gif
        self.gif_url = "%s/image/%s" % (self.url, self.gif.pk)

        # JPEG
        f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
        jpeg = self.spot.spotimage_set.create( description = "This is the JPEG test", image = File(f) )
        jpeg.save()
        f.close()

        self.jpeg = jpeg
        self.jpeg_url = "%s/image/%s" % (self.url, self.jpeg.pk)

        # PNG
        f = open("%s/../resources/test_png.png" % TEST_ROOT)
        png = self.spot.spotimage_set.create( description = "This is the PNG test", image = File(f) )
        png.save()
        f.close()

        self.png = png
        self.png_url = "%s/image/%s" % (self.url, self.png.pk)


    def test_bad_json(self):
        c = Client()

        #GIF
        response = c.put(self.gif_url, 'this is just text', content_type="application/json", If_Match = self.spot.etag)
        self.assertEquals(response.status_code, 400, "Rejects non-json")

        #JPEG
        response = c.put(self.jpeg_url, 'this is just text', content_type="application/json", If_Match = self.spot.etag)
        self.assertEquals(response.status_code, 400, "Rejects non-json")

        #PNG
        response = c.put(self.png_url, 'this is just text', content_type="application/json", If_Match = self.spot.etag)
        self.assertEquals(response.status_code, 400, "Rejects non-json")


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

