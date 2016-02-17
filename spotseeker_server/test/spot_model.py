""" Copyright 2012, 2013 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from django.test import TestCase
from django.conf import settings
import random

from spotseeker_server.models import Spot
from django.test.utils import override_settings
from mock import patch
from django.core import cache
from spotseeker_server import models


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                   SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm')
class SpotModelTest(TestCase):

    def test_json(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            name = "This is a test spot: {0}".format(random.random())

            spot = Spot()
            spot.name = name
            spot.save()

            saved_id = spot.pk

            test_spot = Spot.objects.get(pk=saved_id)
            json_data = test_spot.json_data_structure()

            self.assertEqual(json_data["name"], name, "The json structure has the right name")
            self.assertEqual(json_data["id"], saved_id, "The json structure has the right id")
