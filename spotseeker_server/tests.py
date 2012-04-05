from django.utils import unittest

from spotseeker_server.test.spot_form import SpotFormTest
from spotseeker_server.test.spot_model import SpotModelTest
from spotseeker_server.test.spot_put import SpotPUTTest
from spotseeker_server.test.spot_delete import SpotDELETETest
from spotseeker_server.test.spot_post import SpotPOSTTest
from spotseeker_server.test.spot_get import SpotGETTest
from spotseeker_server.test.images.get import SpotImageGETTest
from spotseeker_server.test.images.post import SpotImagePOSTTest
from spotseeker_server.test.images.thumb import ImageThumbTest
from spotseeker_server.test.search.distance import SpotSearchDistanceTest
from spotseeker_server.test.search.fields import SpotSearchFieldTest
from spotseeker_server.test.search.distance_fields import SpotSearchDistanceFieldTest
from spotseeker_server.test.hours.model import SpotHoursModelTest
from spotseeker_server.test.hours.get import SpotHoursGETTest
from spotseeker_server.test.hours.put import SpotHoursPUTTest
from spotseeker_server.test.hours.post import SpotHoursPOSTTest

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
        suite.addTest(SpotSearchFieldTest())
        suite.addTest(SpotSearchDistanceFieldTest())
        suite.addTest(SpotHoursModelTest())


