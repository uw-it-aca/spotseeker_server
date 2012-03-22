from django.utils import unittest

from spotseeker_server.test.spot_form import SpotFormTest
from spotseeker_server.test.spot_model import SpotModelTest
from spotseeker_server.test.spot_put import SpotPUTTest
from spotseeker_server.test.spot_delete import SpotDELETETest

class SpotSeekerTests(unittest.TestCase):
    def suite(self):
        suite = unittest.TestSuite()
        suite.addTest(SpotFormTest())
        suite.addTest(SpotModelTest())
        suite.addTest(SpotPUTTest())
        suite.addTest(SpotDELETETest())

