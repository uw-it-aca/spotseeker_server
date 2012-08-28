from django.test import TestCase
from django.conf import settings
import random

from spotseeker_server.models import Spot


class SpotModelTest(TestCase):

    def test_json(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                           SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm'):
            name = "This is a test spot: {0}".format(random.random())

            spot = Spot()
            spot.name = name
            spot.save()

            saved_id = spot.pk

            test_spot = Spot.objects.get(pk=saved_id)
            json_data = test_spot.json_data_structure()

            self.assertEqual(json_data["name"], name, "The json structure has the right name")
            self.assertEqual(json_data["id"], saved_id, "The json structure has the right id")
