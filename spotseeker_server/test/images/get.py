from django.utils import unittest
from django.test.client import Client
from django.core.files import File
from spotseeker_server.models import Spot, SpotImage
from cStringIO import StringIO
from PIL import Image
from os.path import abspath, dirname
import random

TEST_ROOT = abspath(dirname(__file__))

class SpotImageGETTest(unittest.TestCase):
    def setUp(self):
        spot = Spot.objects.create( name = "This is to test getting images" )
        spot.save()
        self.spot = spot

        f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
        gif = SpotImage.objects.create( description = "This is the GIF test", spot=spot, image = File(f) )
        gif.save()
        f.close()

        self.gif = gif

        f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
        jpeg = SpotImage.objects.create( description = "This is the JPEG test", spot=spot, image = File(f) )
        jpeg.save()
        f.close()

        self.jpeg = jpeg

        f = open("%s/../resources/test_png.png" % TEST_ROOT)
        png = SpotImage.objects.create( description = "This is the PNG test", spot=spot, image = File(f) )
        png.save()
        f.close()

        self.png = png

        self.url = '/api/v1/spot/{0}/image'.format(self.spot.pk)
        self.url = self.url

    def test_jpeg(self):
        c = Client()
        response = c.get("{0}/{1}".format(self.url, self.jpeg.pk))
        data = StringIO(response.content)
        im = Image.open(data)
        self.assertEquals(response["Content-type"], "image/jpeg", "Content type is jpeg")

        orig = Image.open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)

        self.assertEquals(im.size[0], orig.size[0], "Width matches original")
        self.assertEquals(im.size[1], orig.size[1], "Height matches original")
        self.assertEquals(im.format, 'JPEG', "Actual type of image is jpeg")

    def test_gif(self):
        c = Client()
        response = c.get("{0}/{1}".format(self.url, self.gif.pk))
        data = StringIO(response.content)
        im = Image.open(data)
        self.assertEquals(response["Content-type"], "image/gif", "Content type is gif")

        orig = Image.open("%s/../resources/test_gif.gif" % TEST_ROOT)

        self.assertEquals(im.size[0], orig.size[0], "Width matches original")
        self.assertEquals(im.size[1], orig.size[1], "Height matches original")
        self.assertEquals(im.format, 'GIF', "Actual type of image is gif")

    def test_png(self):
        c = Client()
        response = c.get("{0}/{1}".format(self.url, self.png.pk))
        data = StringIO(response.content)
        im = Image.open(data)
        self.assertEquals(response["Content-type"], "image/png", "Content type is png")

        orig = Image.open("%s/../resources/test_png.png" % TEST_ROOT)

        self.assertEquals(im.size[0], orig.size[0], "Width matches original")
        self.assertEquals(im.size[1], orig.size[1], "Height matches original")
        self.assertEquals(im.format, 'PNG', "Actual type of image is png")

