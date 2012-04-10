from django.utils import unittest
from django.test.client import Client
from spotseeker_server.models import Spot

class SpotImageDELETETest(unittest.TestCase):
    def setUp(self):
        spot = Spot.objects.create( name = "This is to test deleting images" )
        spot.save()
        self.spot = spot

        self.url = '/api/v1/spot/{0}'.format(self.spot.pk)

        c = Client()
        f = open('test/resources/test_jpeg.jpg')
        response = c.post(self.url, { "description": "This is a jpeg", "image": f })
        f.close()

        f = open('test/resources/test_gif.gif')
        response = c.post(self.url, { "description": "This is a gif", "image": f })
        f.close()

        f = open('test/resources/test_png.png')
        response = c.post(self.url, { "description": "This is a png", "image": f })
        f.close()
