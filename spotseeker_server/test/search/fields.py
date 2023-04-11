# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from spotseeker_server.test import SpotServerTestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot, SpotExtendedInfo, SpotType
import simplejson as json
from django.test.utils import override_settings
from mock import patch
from spotseeker_server import models


@override_settings(SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok")
class SpotSearchFieldTest(SpotServerTestCase):
    @classmethod
    def setUpClass(self):
        # .new_spot() is from spotseeker_server.test.SpotServerTestCase
        # (__init__.py)
        self.spot1 = self.new_spot("This is a searchable Name - OUGL")

        self.spot2 = self.new_spot("This OUGL is an alternative spot")

        self.spot3 = self.new_spot("3rd spot")

        self.spot4 = self.new_spot("OUGL - 3rd spot in the site")

        self.spot5 = self.new_spot("Has whiteboards")
        self.add_ei_to_spot(self.spot5, has_whiteboards=True)

        self.spot6 = self.new_spot("Has no whiteboards")
        self.add_ei_to_spot(self.spot6, has_whiteboards=False)

        self.spot7 = self.new_spot(
            "Text search for the title - Odegaard "
            "Undergraduate Library and Learning Commons"
        )
        self.add_ei_to_spot(self.spot7, has_whiteboards=True)

        self.natural = self.new_spot("Has field value: natural")
        self.add_ei_to_spot(self.natural, lightingmultifieldtest="natural")

        self.artificial = self.new_spot("Has field value: artificial")
        self.add_ei_to_spot(
            self.artificial, lightingmultifieldtest="artificial"
        )

        self.other = self.new_spot("Has field value: other")
        self.add_ei_to_spot(self.other, lightingmultifieldtest="other")

        # It doesn't actually have a field value
        self.darkness = self.new_spot("Has field value: darkness")

        self.american_food_spot = self.new_spot("American Food")
        self.add_ei_to_spot(
            self.american_food_spot,
            s_cuisine_american="true",
            app_type="food",
            s_payment_husky="true",
        )

        self.bbq_food_spot = self.new_spot("BBQ")
        self.add_ei_to_spot(
            self.bbq_food_spot,
            s_cuisine_bbq="true",
            s_payment_cash="true",
            app_type="food",
        )

        self.food_court_spot = self.new_spot("Food Court")
        self.add_ei_to_spot(
            self.food_court_spot,
            s_cuisine_american="true",
            s_cuisine_bbq="true",
            app_type="food",
            s_payment_husky="true",
            s_payment_cash="true",
        )

        self.chinese_food_spot = self.new_spot("Chinese Food")
        self.add_ei_to_spot(
            self.chinese_food_spot,
            s_cuisine_chinese="true",
            app_type="food",
            s_payment_cash="true",
        )

        self.study_spot = self.new_spot("Study Here!")
        self.add_ei_to_spot(self.study_spot, has_whiteboards="true")

        cafe_type = SpotType.objects.get_or_create(name="cafe_testing")[0]
        open_type = SpotType.objects.get_or_create(name="open_testing")[0]
        never_used_type = SpotType.objects.get_or_create(
            name="never_used_testing"
        )[0]

        self.spot8 = self.new_spot("Spot8 is a cafe for multi type test")
        self.spot8.spottypes.add(cafe_type)

        self.spot9 = self.new_spot(
            "Spot 9 is an Open space for multi type " "test"
        )
        self.spot9.spottypes.add(open_type)

        self.spot10 = self.new_spot(
            "Spot 10 is an Open cafe for " "multi type test"
        )
        self.spot10.spottypes.add(cafe_type)
        self.spot10.spottypes.add(open_type)

        self.spot11 = self.new_spot("Spot 11 should never get returned")
        self.spot11.spottypes.add(never_used_type)

        self.spot12 = self.new_spot("Room A403", building_name="Building A")

        self.spot13 = self.new_spot("Room A589", building_name="Building A")

        self.spot14 = self.new_spot("Room B328", building_name="Building B")

        self.spot15 = self.new_spot("Room B943", building_name="Building B")

        self.spot16 = self.new_spot("Room C483", building_name="Building C")

    def test_fields(self):
        response = self.client.get("/api/v1/spot", {"name": "OUGL"})

        self.assertEqual(response.status_code, 200, "Accepts name query")
        self.assertJsonHeader(response)
        spots = json.loads(response.content)
        expected = [self.spot1, self.spot2, self.spot4]
        self.assertSpotsToJson(expected, spots)

        response = self.client.get(
            "/api/v1/spot", {"extended_info:has_whiteboards": True}
        )
        self.assertEqual(
            response.status_code, 200, "Accepts whiteboards query"
        )

        self.assertJsonHeader(response)
        spots = json.loads(response.content)
        expected = [self.spot5, self.spot7]
        self.assertSpotsToJson(expected, spots)

        response = self.client.get(
            "/api/v1/spot",
            {"extended_info:has_whiteboards": True, "name": "odegaard under"},
        )
        self.assertEqual(
            response.status_code, 200, "Accepts whiteboards + name query"
        )
        self.assertJsonHeader(response)

        spots = json.loads(response.content)
        self.assertSpotsToJson([self.spot7], spots)

    def test_only_invalid_field(self):
        """
        Test that specifying ONLY an invalid parameter does not
        allow the search to proceed, similar to when no parameters
        are given.
        """
        response = self.client.get("/api/v1/spot", {"invalid_field": "OUGL"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {
                "error": "missing required parameters for "
                "this type of search"
            },
        )

    def test_some_invalid_field(self):
        """
        Test that specifying an invalid field and a valid field still allows
        the search to proceed, ignoring the invalid field.
        """
        params = {"name": "OUGL", "invalid_param": "foo_bar"}
        response = self.client.get("/api/v1/spot", params)
        self.assertEqual(response.status_code, 200)
        spots = json.loads(response.content)
        expected = [self.spot1, self.spot2, self.spot4]
        self.assertSpotsToJson(expected, spots)

    def test_invalid_extended_info(self):
        response = self.client.get(
            "/api/v1/spot", {"extended_info:invalid_field": "OUGL"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertJsonHeader(response)
        self.assertEqual(
            response.content.decode(), "[]", "Should return no matches"
        )

    def test_multi_value_field(self):
        # Natural lighting
        response = self.client.get(
            "/api/v1/spot", {"extended_info:lightingmultifieldtest": "natural"}
        )
        self.assertJsonHeader(response)
        spots = json.loads(response.content)
        self.assertSpotsToJson([self.natural], spots)
        # Artificial light
        response = self.client.get(
            "/api/v1/spot",
            {"extended_info:lightingmultifieldtest": "artificial"},
        )
        self.assertJsonHeader(response)
        spots = json.loads(response.content)
        self.assertSpotsToJson([self.artificial], spots)
        # Other lighting
        response = self.client.get(
            "/api/v1/spot", {"extended_info:lightingmultifieldtest": "other"}
        )
        self.assertJsonHeader(response)
        spots = json.loads(response.content)
        self.assertSpotsToJson([self.other], spots)
        # Other + natural
        response = self.client.get(
            "/api/v1/spot",
            {"extended_info:lightingmultifieldtest": ("other", "natural")},
        )
        self.assertJsonHeader(response)
        spots = json.loads(response.content)
        self.assertSpotsToJson([self.other, self.natural], spots)

    def test_spot_by_id(self):
        """Test getting spots by ID"""
        # For this next test, make sure
        # we're trying to get spots that actually exist.
        spot_models = Spot.objects.all()[0:4]
        ids = [spot.pk for spot in spot_models]

        response = self.client.get("/api/v1/spot", {"id": ids})
        self.assertJsonHeader(response)
        spots = json.loads(response.content)
        self.assertSpotsToJson(spot_models, spots)

    def test_extended_info_or(self):
        """Tests searches for Spots with
        extended_info that has multiple values."""
        response = self.client.get(
            "/api/v1/spot",
            {
                "extended_info:or:s_cuisine_bbq": "true",
                "extended_info:or:s_cuisine_american": "true",
                "extended_info:app_type": "food",
            },
        )
        self.assertEqual(response.status_code, 200)
        spots = json.loads(response.content)
        expected = [
            self.american_food_spot,
            self.bbq_food_spot,
            self.food_court_spot,
        ]
        self.assertSpotsToJson(expected, spots)

    def test_multi_type_spot(self):
        response = self.client.get("/api/v1/spot", {"type": "cafe_testing"})
        self.assertJsonHeader(response)
        spots = json.loads(response.content)
        self.assertSpotsToJson([self.spot8, self.spot10], spots)

        response = self.client.get("/api/v1/spot", {"type": "open_testing"})
        self.assertJsonHeader(response)
        spots = json.loads(response.content)
        self.assertSpotsToJson([self.spot9, self.spot10], spots)

        response = self.client.get(
            "/api/v1/spot", {"type": ["cafe_testing", "open_testing"]}
        )
        self.assertJsonHeader(response)
        spots = json.loads(response.content)
        self.assertSpotsToJson([self.spot8, self.spot9, self.spot10], spots)

    def test_multi_building_search(self):
        """Tests to be sure searching for spots in
        multiple buildings returns spots for all buildings.
        """
        response = self.client.get(
            "/api/v1/spot", {"building_name": ["Building A", "Building B"]}
        )
        spots = json.loads(response.content)
        expected = [self.spot12, self.spot13, self.spot14, self.spot15]
        self.assertSpotsToJson(expected, spots)

    def test_extended_info_or_gouping(self):
        """Tests searches for Spots with
        extended_info that has multiple values."""
        response = self.client.get(
            "/api/v1/spot",
            {
                "extended_info:app_type": "food",
                "extended_info:or_group:cuisine": [
                    "s_cuisine_bbq",
                    "s_cuisine_american",
                ],
            },
        )
        self.assertEqual(response.status_code, 200)
        spots = json.loads(response.content)
        expected = [
            self.american_food_spot,
            self.bbq_food_spot,
            self.food_court_spot,
        ]
        self.assertSpotsToJson(expected, spots)

    def test_extended_info_or_gouping_many(self):
        """Tests searches for Spots with
        extended_info that has multiple values."""
        response = self.client.get(
            "/api/v1/spot",
            {
                "extended_info:app_type": "food",
                "extended_info:or_group:groupone": [
                    "s_cuisine_bbq",
                    "s_cuisine_american",
                ],
                "extended_info:or_group:grouptwo": [
                    "s_payment_husky",
                    "s_payment_cash",
                ],
            },
        )
        self.assertEqual(response.status_code, 200)
        spots = json.loads(response.content)
        expected = [
            self.american_food_spot,
            self.bbq_food_spot,
            self.food_court_spot,
        ]
        self.assertSpotsToJson(expected, spots)
