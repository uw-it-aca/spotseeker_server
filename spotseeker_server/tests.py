from django.utils import unittest

from spotseeker_server.test.spot_form import SpotFormTest
from spotseeker_server.test.spot_model import SpotModelTest
from spotseeker_server.test.spot_put import SpotPUTTest
from spotseeker_server.test.spot_delete import SpotDELETETest
from spotseeker_server.test.spot_post import SpotPOSTTest
from spotseeker_server.test.spot_get import SpotGETTest
from spotseeker_server.test.spot_post_image import SpotImagePOSTTest
from spotseeker_server.test.image_thumb import ImageThumbTest
from spotseeker_server.test.search.distance import SpotSearchDistanceTest

class SpotSeekerTests(unittest.TestCase):
    def suite(self):
        suite = unittest.TestSuite()
        suite.addTest(SpotFormTest())
        suite.addTest(SpotModelTest())
        suite.addTest(SpotPUTTest())
        suite.addTest(SpotDELETETest())
        suite.addTest(SpotPOSTTest())
        suite.addTest(SpotGETTest())
        suite.addTest(SpotImagePOSTTest())
        suite.addTest(ImageThumbTest())
        suite.addTest(SpotSearchDistanceTest())

