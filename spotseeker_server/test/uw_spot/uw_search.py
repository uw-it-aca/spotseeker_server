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
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.utils.unittest import skipUnless
from spotseeker_server.models import Spot, SpotExtendedInfo
from spotseeker_server.cache import memory_cache
import json


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
class UWSearchTest(TestCase):
    """ Tests that special Extended Info searches behave properly.
    """

    def setUp(self):
        # create a spot without app_type
        self.spot1 = Spot.objects.create(name="no app type spot", capacity=4)
        # create a spot with app_type
        self.spot2 = Spot.objects.create(name="food spot", capacity=4)
        self.spot2.save()
        self.ei2 = SpotExtendedInfo.objects.create(
            spot=self.spot2, key="app_type", value="food")
        # create a spot with some other app_type
        self.spot3 = Spot.objects.create(
            name="resource checkout spot", capacity=4)
        self.ei3 = SpotExtendedInfo.objects.create(
            spot=self.spot3, key="app_type", value="checkout")
        # create a spot with a group
        self.spot4 = Spot.objects.create(
            name="spot within our group", capacity=4
        )
        self.ei4 = SpotExtendedInfo.objects.create(
            spot=self.spot4, key='uwgroup', value='our_group'
        )
        # create spot with another group
        self.spot5 = Spot.objects.create(
            name='spot within their group', capacity=4
        )
        self.ei5 = SpotExtendedInfo.objects.create(
            spot=self.spot5, key='uwgroup', value='their_group'
        )
        # create a test Client
        self.client = Client()
        memory_cache.clear_cache()

    def tearDown(self):
        self.spot1.delete()
        self.spot2.delete()
        self.spot3.delete()
        self.spot4.delete()
        self.spot5.delete()
        memory_cache.clear_cache()

    def test_app_type(self):
        """ Tests searching with an app_type query param.
        """
        # make a GET search passing app_type food
        response = self.client.get(
            "/api/v1/spot", {"capacity": 4, "extended_info:app_type": "food"})
        # assert a 200 JSON response
        self.assertEqual(200, response.status_code)
        self.assertEquals(response["Content-Type"], "application/json")
        # assert the right number of spots are returned
        spots = json.loads(response.content)
        self.assertEqual(1, len(spots))
        # assert the correct spot was returned
        self.assertTrue(self.spot1.json_data_structure() not in spots)
        self.assertTrue(self.spot2.json_data_structure() in spots)
        self.assertTrue(self.spot3.json_data_structure() not in spots)

    @skipUnless(
        getattr(settings, 'SPOTSEEKER_SEARCH_FILTERS', False) and
        settings.SPOTSEEKER_SEARCH_FILTERS ==
        ['spotseeker_server.org_filters.uw_search.Filter'],
        "Skip unless the right search filter is defined in settings"
    )
    def test_no_app_type(self):
        """ Tests searching with no app_type query param.
        """
        # make a GET search without passing an app_type at all
        response = self.client.get("/api/v1/spot", {"capacity": 4})
        # assert a 200 JSON response
        self.assertEqual(200, response.status_code)
        self.assertEquals(response["Content-Type"], "application/json")
        # assert the right number of spots are returned
        spots = json.loads(response.content)
        self.assertEqual(3, len(spots))
        # assert the correct spot was returned
        self.assertTrue(self.spot1.json_data_structure() in spots)
        self.assertTrue(self.spot2.json_data_structure() not in spots)
        self.assertTrue(self.spot3.json_data_structure() not in spots)
        self.assertTrue(self.spot4.json_data_structure() in spots)
        self.assertTrue(self.spot5.json_data_structure() in spots)

    @skipUnless(
        getattr(settings, 'SPOTSEEKER_SEARCH_FILTERS', False) and
        settings.SPOTSEEKER_SEARCH_FILTERS ==
        ['spotseeker_server.org_filters.uw_search.Filter'],
        "Skip unless the right search filter is defined in settings"
    )
    def test_single_group_filtering(self):
        response = self.client.get("/api/v1/spot",
                                   {"extended_info:uwgroup": "our_group"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(response["Content-Type"], "application/json")

        spots = json.loads(response.content)
        self.assertEqual(1, len(spots))
        self.assertTrue(self.spot1.json_data_structure() not in spots)
        self.assertTrue(self.spot2.json_data_structure() not in spots)
        self.assertTrue(self.spot3.json_data_structure() not in spots)
        self.assertTrue(self.spot4.json_data_structure() in spots)

    @skipUnless(
        getattr(settings, 'SPOTSEEKER_SEARCH_FILTERS', False) and
        settings.SPOTSEEKER_SEARCH_FILTERS ==
        ['spotseeker_server.org_filters.uw_search.Filter'],
        "Skip unless the right search filter is defined in settings"
    )
    def test_multiple_group_filtering(self):
        response = self.client.get("/api/v1/spot",
                                   {"extended_info:uwgroup":
                                    ["our_group", "their_group"]})
        self.assertEqual(200, response.status_code)
        self.assertEqual(response["Content-Type"], "application/json")

        spots = json.loads(response.content)
        self.assertEqual(2, len(spots))
        self.assertTrue(self.spot1.json_data_structure() not in spots)
        self.assertTrue(self.spot2.json_data_structure() not in spots)
        self.assertTrue(self.spot3.json_data_structure() not in spots)
        self.assertTrue(self.spot4.json_data_structure() in spots)
        self.assertTrue(self.spot5.json_data_structure() in spots)
