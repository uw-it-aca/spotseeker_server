# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

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
from spotseeker_server.models import Spot, SpotExtendedInfo, SpotType
import simplejson as json
from django.test.utils import override_settings
from mock import patch
from spotseeker_server import models


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
class SpotSearchCapacityTest(SpotServerTestCase):
    def test_capacity(self):

        # Create spots with 1, 2, 3, 4, 50 capacity, respectively
        caps = (1, 2, 3, 4, 50)
        ALL_SPOTS =\
            [self.new_spot('capacity: %s' % c, capacity=c) for c in caps]
        spot1, spot2, spot3, spot4, spot5 = ALL_SPOTS

        # Test with unspecified capacity
        c = self.client
        response = c.get(
            "/api/v1/spot",
            {'capacity': '',
             'name':
             'capacity'}
        )
        self.assertJsonHeader(response)
        spots = json.loads(response.content)
        # Should return all spots
        self.assertSpotsToJson(ALL_SPOTS, spots,
                               'Expected all spots to be returned when '
                               'capacity is unspecified')

        response = c.get("/api/v1/spot", {'capacity': '1'})
        self.assertJsonHeader(response)
        spots = json.loads(response.content)
        self.assertSpotsToJson(ALL_SPOTS, spots,
                               'Expected all spots to be returned for'
                               'capacity: 1')

        response = c.get("/api/v1/spot", {'capacity': '49'})
        self.assertJsonHeader(response)
        spots = json.loads(response.content)
        self.assertSpotsToJson([spot5], spots,
                               'Should only find the big spot')

        response = c.get("/api/v1/spot", {'capacity': '501'})
        self.assertJsonHeader(response)
        spots = json.loads(response.content)
        self.assertSpotsToJson([], spots,
                               "Shouldn't have found any spots")

        # TODO: move this somewhere else
        response = c.get("/api/v1/spot",
                         {'capacity': '1',
                          'distance': '100',
                          'limit': '4'}
                         )
        # testing sorting by distance, which is impossible given no center
        self.assertEquals(response.status_code, 400)
