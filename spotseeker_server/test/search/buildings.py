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

from spotseeker_server.test import SpotServerTestCase
from django.conf import settings
from django.test.utils import override_settings
import simplejson as json


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
class BuildingSearchTest(SpotServerTestCase):
    """ Tests the /api/v1/buildings interface.
    """

    def setUp(self):
        self.spot1 = self.new_spot('Spot on campus A.',
                                   building_name='Building 1')

        self.spot1_2 = self.new_spot("Other spot on campus A.",
                                     building_name="Building 2")

        self.spot2 = self.new_spot("Spot on campus B.",
                                   building_name="Building3")

        self.spot3 = self.new_spot("Another Spot on campus B.",
                                   building_name="Building 4")

        self.spot4 = self.new_spot("Spot on campus C.",
                                   building_name="Building 5")

        self.spot5 = self.new_spot("Here is a spot on campus D.",
                                   building_name='Building 6')

        self.spot6 = self.new_spot('Another spot on campus C.',
                                   building_name='Building 7')

        self.spot7 = self.new_spot('Another spot on campus D.',
                                   building_name='Building 8')

        self.add_ei_to_spot(self.spot1, campus='campus_a', app_type='food')
        self.add_ei_to_spot(self.spot1_2, campus='campus_a')
        self.add_ei_to_spot(self.spot2, campus='campus_b')
        self.add_ei_to_spot(self.spot3, campus='campus_b')
        self.add_ei_to_spot(self.spot4, campus='campus_c')
        self.add_ei_to_spot(self.spot5, campus='campus_d', app_type='food')
        self.add_ei_to_spot(self.spot6, campus='campus_c', app_type='book')
        self.add_ei_to_spot(self.spot7, campus='campus_d', app_type='food')

    def tearDown(self):
        self.spot1.delete()
        self.spot1_2.delete()
        self.spot2.delete()
        self.spot3.delete()
        self.spot4.delete()
        self.spot5.delete()
        self.spot6.delete()

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
        """ Tests that the correct buildings are returned when campus extended
        info is passed.

            This test was implemented against the UW Search Filter, so it was
            moved to tests/search/uw_buildings.py as
            test_uw_buildings_for_campus. This is now a stub for someone to
            write a test against the Default search filter.
        """
        pass

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
        """ Tests that the correct buildings are returned when campus extended
        info is passed.

            This test was implemented against the UW Search Filter, so it was
            moved to tests/search/uw_buildings.py as
            test_uw_extended_info_campus. This is now a stub for someone to
            write a test against the Default search filter.
        """
        pass
