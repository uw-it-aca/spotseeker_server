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

from django.conf import settings
from django.test.utils import override_settings
from spotseeker_server.models import Spot, SpotExtendedInfo
import simplejson as json
from mock import patch
from spotseeker_server import models
from spotseeker_server.test import ServerTest


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
class BuildingSearchTest(ServerTest):
    """ Tests the /api/v1/buildings interface.
    """

    def setUp(self):
        super(BuildingSearchTest, self).setUp()
        self.spot1 = Spot.objects.create(name="Spot on campus A.",
                                         building_name="Building 1")
        self.spot1_2 = Spot.objects.create(name="Other spot on campus A.",
                                           building_name="Building 2")
        self.spot2 = Spot.objects.create(name="Spot on campus B.",
                                         building_name="Building3")
        self.spot3 = Spot.objects.create(name="Another Spot on campus B.",
                                         building_name="Building 4")
        self.spot4 = Spot.objects.create(name="Spot on campus C.",
                                         building_name="Building 5")
        self.spot5 = Spot.objects.create(name="Here is a spot on campus D.",
                                         building_name='Building 6')
        self.spot6 = Spot.objects.create(name='Another spot on campus C.',
                                         building_name='Building 7')
        self.spot7 = Spot.objects.create(name='Another spot on campus D.',
                                         building_name='Building 8')

        self.spot1_campus = SpotExtendedInfo.objects.create(spot=self.spot1,
                                                            key="campus",
                                                            value="campus_a")
        self.spot1_campus.save()
        self.spot1_app_type = SpotExtendedInfo.objects.create(spot=self.spot1,
                                                              key='app_type',
                                                              value='food')
        self.spot1_app_type.save()
        self.spot1_2_campus = SpotExtendedInfo.objects.create(
            spot=self.spot1_2,
            key='campus',
            value='campus_a'
        )
        self.spot1_2_campus.save()
        self.spot2_campus = SpotExtendedInfo.objects.create(spot=self.spot2,
                                                            key="campus",
                                                            value="campus_b")
        self.spot2_campus.save()
        self.spot3_campus = SpotExtendedInfo.objects.create(spot=self.spot3,
                                                            key="campus",
                                                            value="campus_b")
        self.spot3_campus.save()
        self.spot4_campus = SpotExtendedInfo.objects.create(spot=self.spot4,
                                                            key="campus",
                                                            value="campus_c")
        self.spot4_campus.save()
        self.spot5_campus = SpotExtendedInfo.objects.create(spot=self.spot5,
                                                            key='campus',
                                                            value='campus_d')
        self.spot5_campus.save()
        self.spot5_app_type = SpotExtendedInfo.objects.create(spot=self.spot5,
                                                              key='app_type',
                                                              value='food')
        self.spot6_campus = SpotExtendedInfo.objects.create(spot=self.spot6,
                                                            key='campus',
                                                            value='campus_c')
        self.spot6_campus.save()
        self.spot6_app_type = SpotExtendedInfo.objects.create(spot=self.spot6,
                                                              key='app_type',
                                                              value='book')
        self.spot6_app_type.save()
        self.spot7_campus = SpotExtendedInfo.objects.create(spot=self.spot7,
                                                            key='campus',
                                                            value='campus_d')
        self.spot7_campus.save()
        self.spot7_app_type = SpotExtendedInfo.objects.create(spot=self.spot7,
                                                              key='app_type',
                                                              value='food')
        self.spot7_app_type.save()

    def test_content_type(self):
        c = self.client
        url = "/api/v1/buildings"
        response = c.get(url)
        self.assertEquals(response["Content-Type"],
                          "application/json",
                          "Has the json header")

    def test_get_all_buildings(self):
        c = self.client
        # TODO: Even though this works, we do not recommend using this method.
        # You should be passing at least one query param.
        response = c.get("/api/v1/buildings")
        buildings = json.loads(response.content)
        self.assertEquals(len(buildings), 8)

    def test_buildings_for_campus(self):
        c = self.client

        response = c.get("/api/v1/buildings/", {"campus": "campus_a"})
        buildings = json.loads(response.content)

        self.assertEquals(len(buildings), 1)
        # Assert that the building returned is not from the tacoma campus.
        self.assertNotEqual(buildings[0], self.spot1.building_name)
        # Assert that the building returned is from the seattle campus.
        self.assertEquals(buildings[0], self.spot1_2.building_name)

        response = c.get("/api/v1/buildings", {"campus": "campus_b"})
        buildings = json.loads(response.content)

        self.assertEquals(len(buildings), 2)
        for building in buildings:
            # Assert that the building returned is not from the seattle campus.
            self.assertNotEqual(building, self.spot1.building_name)

    def test_buildings_for_app_type(self):
        c = self.client

        response = c.get(
            '/api/v1/buildings/',
            {'extended_info:app_type': 'food'}
        )
        buildings = json.loads(response.content)

        self.assertEqual(len(buildings), 3)
        self.assertEqual(buildings[0], self.spot1.building_name)
        self.assertEqual(buildings[1], self.spot5.building_name)

        response = c.get(
            '/api/v1/buildings/',
            {'extended_info:app_type': 'book'}
        )
        buildings = json.loads(response.content)
        self.assertEqual(len(buildings), 1)
        self.assertEqual(buildings[0], self.spot6.building_name)

    def test_buildings_for_app_type_and_campus(self):
        c = self.client

        response = c.get(
            '/api/v1/buildings/',
            {'extended_info:app_type': 'food',
             'campus': 'campus_a'}
        )
        buildings = json.loads(response.content)
        self.assertEqual(len(buildings), 1)
        self.assertEqual(buildings[0], self.spot1.building_name)

        response = c.get(
            '/api/v1/buildings/',
            {'extended_info:app_type': 'book',
             'campus': 'campus_c'}
        )
        buildings = json.loads(response.content)
        self.assertEqual(len(buildings), 1)
        self.assertEqual(buildings[0], self.spot6.building_name)

        response = c.get('/api/v1/buildings/',
                         {'extended_info:app_type': 'food',
                          'campus': 'campus_d'}
                         )
        buildings = json.loads(response.content)
        self.assertEqual(len(buildings), 2)
        self.assertEqual(buildings[0], self.spot5.building_name)
        self.assertEqual(buildings[1], self.spot7.building_name)

    def test_extended_info_campus(self):
        c = self.client

        response = c.get('/api/v1/buildings/',
                         {'extended_info:campus': 'campus_c'})
        buildings = json.loads(response.content)
        self.assertEqual(len(buildings), 1)
        self.assertEqual(buildings[0], self.spot4.building_name)

        response = c.get(
            '/api/v1/buildings/',
            {'extended_info:campus': 'campus_d',
             'extended_info:app_type': 'food'}
        )
        buildings = json.loads(response.content)
        self.assertEqual(len(buildings), 2)
