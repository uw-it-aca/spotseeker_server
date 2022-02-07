# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.conf import settings
import random

from spotseeker_server.models import Spot
from django.test.utils import override_settings
from mock import patch
from spotseeker_server import models


@override_settings(
    SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok",
    SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms.spot."
    "DefaultSpotForm",
)
class SpotModelTest(TestCase):
    def test_json(self):
        name = "This is a test spot: {0}".format(random.random())

        spot = Spot()
        spot.name = name
        spot.save()

        saved_id = spot.pk

        test_spot = Spot.objects.get(pk=saved_id)
        json_data = test_spot.json_data_structure()

        self.assertEqual(json_data["name"], name)
        self.assertEqual(json_data["id"], saved_id)
