from django.utils import unittest
from django.conf import settings
import random

from spotseeker_server.models import Spot

class SpotModelTest(unittest.TestCase):
    settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok';
    def test_json(self):
        name = "This is a test spot: {0}".format(random.random())

        spot = Spot()
        spot.name = name
        spot.save()

        saved_id = spot.pk

        test_spot = Spot.objects.get(pk=saved_id)
        json_data = test_spot.json_data_structure()

        self.assertEqual(json_data["name"], name, "The json structure has the right name")
        self.assertEqual(json_data["id"], saved_id, "The json structure has the right id")

