from django.utils import unittest
from django.test.client import Client
from django.core.files import File
from spotseeker_server.models import Spot, SpotImage
from os.path import abspath, dirname

TEST_ROOT = abspath(dirname(__file__))

class SpotImageDELETETest(unittest.TestCase):
    def setUp(self):
        spot = Spot.objects.create( name = "This is to test getting images" )
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

    def test_bad_url(self):
        c = Client()
        response = c.delete(self.gif_url)
        self.assertEquals(response.status_code, 404, "Rejects an invalid url")

        response = c.delete(self.jpeg_url)
        self.assertEquals(response.status_code, 404, "Rejects an invalid url")
        
        response = c.delete(self.png_url)
        self.assertEquals(response.status_code, 404, "Rejects an invalid url")

    def test_invalid_id_too_high(self):
        c = Client()

        #GIF
        test_gif_id = self.gif.pk + 10000
        test_url = "/api/v1/spot/%s/image/%s" % (self.url, test_gif_id)
        response = c.delete(test_url)
        self.assertEquals(response.status_code, 404, "Rejects a not-yet existant url")

        #JPEG
        test_jpeg_id = self.jpeg.pk + 10000
        test_url = "/api/v1/spot/%s/image/%s" % (self.url, test_jpeg_id)
        response = c.delete(test_url)
        self.assertEquals(response.status_code, 404, "Rejects a not-yet existant url")

        #PNG
        test_png_id = self.png.pk + 10000
        test_url = "/api/v1/spot/%s/image/%s" % (self.url, test_png_id)
        response = c.delete(test_url)
        self.assertEquals(response.status_code, 404, "Rejects a not-yet existant url")

    def test_actual_delete_with_etag(self):
        c = Client()

        #GIF
        response = c.get(self.gif_url)
        etag = response["ETag"]

        response = c.delete(self.gif_url, If_Match=etag)

        self.assertEquals(response.status_code, 410, "Gives a GONE in response to a valid delete")

        response = c.get(self.gif_url)
        self.assertEquals(response.status_code, 404, "Gives a 404 on GET after a delete")

        response = c.delete(self.gif_url)
        self.assertEquals(response.status_code, 404, "Gives a 404 on DELETE after a delete")

        try:
            test_gif= SpotImage.objects.get(pk=self.gif.pk)
        except Exception as e:
            test_gif= None

        self.assertIsNone(test_gif, "Can't objects.get a deleted SpotImage")

        #JPEG
        response = c.get(self.jpeg_url)
        etag = response["ETag"]

        response = c.delete(self.jpeg_url, If_Match=etag)

        self.assertEquals(response.status_code, 410, "Gives a GONE in response to a valid delete")

        response = c.get(self.jpeg_url)
        self.assertEquals(response.status_code, 404, "Gives a 404 on GET after a delete")

        response = c.delete(self.jpeg_url)
        self.assertEquals(response.status_code, 404, "Gives a 404 on DELETE after a delete")

        try:
            test_jpeg= SpotImage.objects.get(pk=self.jpeg.pk)
        except Exception as e:
            test_jpeg= None

        self.assertIsNone(test_jpeg, "Can't objects.get a deleted SpotImage")

        #PNG
        response = c.get(self.png_url)
        etag = response["ETag"]

        response = c.delete(self.png_url, If_Match=etag)

        self.assertEquals(response.status_code, 410, "Gives a GONE in response to a valid delete")

        response = c.get(self.png_url)
        self.assertEquals(response.status_code, 404, "Gives a 404 on GET after a delete")

        response = c.delete(self.png_url)
        self.assertEquals(response.status_code, 404, "Gives a 404 on DELETE after a delete")

        try:
            test_png= SpotImage.objects.get(pk=self.png.pk)
        except Exception as e:
            test_png= None

        self.assertIsNone(test_png, "Can't objects.get a deleted SpotImage")

