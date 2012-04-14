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

        f = open("%s/../resources/test_gif.gif" % TEST_ROOT)
        gif = self.spot.spotimage_set.create( description = "This is the GIF test", image = File(f) )
        gif.save()
        f.close()

        self.gif = gif

        f = open("%s/../resources/test_jpeg.jpg" % TEST_ROOT)
        jpeg = self.spot.spotimage_set.create( description = "This is the JPEG test", image = File(f) )
        jpeg.save()
        f.close()

        self.jpeg = jpeg

        f = open("%s/../resources/test_png.png" % TEST_ROOT)
        png = self.spot.spotimage_set.create( description = "This is the PNG test", image = File(f) )
        png.save()
        f.close()

        self.png = png

        self.url = '/api/v1/spot/{0}/image'.format(self.spot.pk)
        self.url = self.url
