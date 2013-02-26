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
from django.test.client import Client
from spotseeker_server.models import Spot, SpotExtendedInfo
import simplejson as json


class BuildingSearchTest(TestCase):
    """ Tests the /api/v1/buildings interface.
    """
    def test_buildings_for_campus(self):
        spot1 = Spot.objects.create(name="Spot on campus A.", building_name="Aay building")
        spot2 = Spot.objects.create(name="Spot on campus B.", building_name="Bee building")
        spot3 = Spot.objects.create(name="Another Spot on campus B.", building_name="Bee building")
        spot4 = Spot.objects.create(name="Yet Another Spot on campus B.", building_name="Cee building")

        spot1_campus = SpotExtendedInfo.objects.create(spot=spot1, key="campus", value="campus_a")
        spot1_campus.save()
        spot2_campus = SpotExtendedInfo.objects.create(spot=spot2, key="campus", value="campus_b")
        spot2_campus.save()
        spot3_campus = SpotExtendedInfo.objects.create(spot=spot3, key="campus", value="campus_b")
        spot2_campus.save()
        spot4_campus = SpotExtendedInfo.objects.create(spot=spot4, key="campus", value="campus_b")
        spot2_campus.save()

        c = Client()

        response = c.get("/api/v1/buildings")
        buildings = json.loads(response.content)
        self.assertEquals(len(buildings), 3, 'Full Building list returns 3 building.')

        response = c.get("/api/v1/buildings", {"campus": "campus_a"})
        buildings = json.loads(response.content)

        self.assertEquals(len(buildings), 1, 'Campus A building list only returns 1 building.')
        # Assert that the building returned is not from the tacoma campus.
        self.assertNotEqual(buildings[0], spot2.building_name, "Returned building is not the one on campus B.")
        # Assert that the building returned is from the seattle campus.
        self.assertEquals(buildings[0], spot1.building_name, "Returned building is the one on campus A.")

        response = c.get("/api/v1/buildings", {"campus": "campus_b"})
        buildings = json.loads(response.content)

        self.assertEquals(len(buildings), 2, 'Campus B building list returns 2 buildings.')
        for building in buildings:
            # Assert that the building returned is not from the seattle campus.
            self.assertNotEqual(building, spot1.building_name, "Returned building is not the one on campus A.")
