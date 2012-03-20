from django.utils import unittest

from spotseeker_server.test.spot_form import SpotFormTest
from spotseeker_server.test.spot_model import SpotModelTest

class SpotSeekerTests(unittest.TestCase):
    def suite(self):
        suite = unittest.TestSuite()
        suite.addTest(SpotFormTest())
        suite.addTest(SpotModelTest())

