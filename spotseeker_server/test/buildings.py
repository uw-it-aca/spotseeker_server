# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot, SpotExtendedInfo
from spotseeker_server import models
from mock import patch
from django.test.utils import override_settings
import simplejson as json


@override_settings(
    SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok",
    SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms."
    "spot.DefaultSpotForm",
)
class BuildingTest(TestCase):
    """Tests getting building information"""

    def setUp(self):
        # creating testing spots
        # keep track of the buildings of the created spots
        self.building_list = []
        self.spots_counts = 100
        for x in range(1, self.spots_counts + 1):
            new_name = "Test Spot " + str(x)
            new_building_name = (
                "Test Building No." + str(x) + "(TB" + str(x) + ")"
            )
            spot = Spot.objects.create(
                name=new_name, building_name=new_building_name
            )
            spot.save()
            self.building_list.append(new_building_name)

    def test_json(self):
        # use the test client to get the building information
        c = Client()
        url = "/api/v1/buildings"
        response = c.get(url)
        self.assertEqual(response["Content-Type"], "application/json")
        # compare the submitted building json against the json got
        # back from the GET request
        post_building = sorted(self.building_list)
        get_building = json.loads(response.content)
        self.assertEqual(post_building, get_building)
