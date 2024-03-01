# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import simplejson as json

from django.test.utils import override_settings
from spotseeker_server.test import SpotServerTestCase
from spotseeker_server.org_filters import SearchFilterChain


@override_settings(
    SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok",
    SPOTSEEKER_SEARCH_FILTERS=(
        "spotseeker_server.org_filters.uw_search.Filter",
    ),
)
class UWBuildingSearchTest(SpotServerTestCase):
    """Tests the /api/v1/buildings interface specifically for the UW Filter."""

    def setUp(self):
        SearchFilterChain._load_filters()
        self.spot1 = self.new_spot(
            "Spot on campus A.", building_name="Building 1"
        )

        self.spot1_2 = self.new_spot(
            "Other spot on campus A.", building_name="Building 2"
        )

        self.spot2 = self.new_spot(
            "Spot on campus B.", building_name="Building3"
        )

        self.spot3 = self.new_spot(
            "Another Spot on campus B.", building_name="Building 4"
        )

        self.spot4 = self.new_spot(
            "Spot on campus C.", building_name="Building 5"
        )

        self.spot5 = self.new_spot(
            "Here is a spot on campus D.", building_name="Building 6"
        )

        self.spot6 = self.new_spot(
            "Another spot on campus C.", building_name="Building 7"
        )

        self.spot7 = self.new_spot(
            "Another spot on campus D.", building_name="Building 8"
        )

        self.add_ei_to_spot(self.spot1, campus="campus_a", app_type="food")
        self.add_ei_to_spot(self.spot1_2, campus="campus_a")
        self.add_ei_to_spot(self.spot2, campus="campus_b")
        self.add_ei_to_spot(self.spot3, campus="campus_b")
        self.add_ei_to_spot(self.spot4, campus="campus_c")
        self.add_ei_to_spot(self.spot5, campus="campus_d", app_type="food")
        self.add_ei_to_spot(self.spot6, campus="campus_c", app_type="book")
        self.add_ei_to_spot(self.spot7, campus="campus_d", app_type="food")

    def tearDown(self):
        self.spot1.delete()
        self.spot1_2.delete()
        self.spot2.delete()
        self.spot3.delete()
        self.spot4.delete()
        self.spot5.delete()
        self.spot6.delete()
        self.spot7.delete()

    def test_uw_buildings_for_campus(self):
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
        self.assertNotIn(self.spot1.building_name, buildings)

    def test_uw_extended_info_campus(self):
        c = self.client

        response = c.get(
            "/api/v1/buildings/", {"extended_info:campus": "campus_c"}
        )
        buildings = json.loads(response.content)
        self.assertEqual(len(buildings), 1)
        self.assertEqual(buildings[0], self.spot4.building_name)

        response = c.get(
            "/api/v1/buildings/",
            {
                "extended_info:campus": "campus_d",
                "extended_info:app_type": "food",
            },
        )
        buildings = json.loads(response.content)
        self.assertEqual(len(buildings), 2)
