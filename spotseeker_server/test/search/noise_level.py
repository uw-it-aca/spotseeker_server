# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.test.utils import override_settings
import simplejson as json
from spotseeker_server.models import Spot, SpotExtendedInfo


def spot_with_noise_level(name, noise_level):
    """Create a spot with the given noise level"""
    spot = Spot.objects.create(name=name)
    spot.spotextendedinfo_set.create(key='noise_level',
                                     value=noise_level)
    return spot


@override_settings(SPOTSEEKER_OAUTH_ENABLED=False)
class NoiseLevelTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.silent_spot = spot_with_noise_level('Silent Spot', 'silent')
        cls.quiet_spot = spot_with_noise_level('Quiet Spot', 'quiet')
        cls.moderate_spot = spot_with_noise_level('Moderate', 'moderate')
        cls.variable_spot = spot_with_noise_level('Var Spot', 'variable')

    @classmethod
    def tearDownClass(cls):
        Spot.objects.all().delete()

    def get_spots_for_noise_levels(self, levels):
        """Do a search for spots with particular noise levels"""
        c = self.client
        response = c.get('/api/v1/spot',
                         {'extended_info:noise_level': levels},
                         content_type='application/json')
        return json.loads(response.content)

    def assertResponseSpaces(self, res_json, spaces):
        """
        Assert that a particular decoded response contains exactly the same
        spaces as 'spaces'.
        """
        def sortfunc(spot_dict):
            return spot_dict['id']
        expected_json = [spot.json_data_structure() for spot in spaces]
        expected_json.sort(key=sortfunc)
        res_json.sort(key=sortfunc)

        self.assertEqual(expected_json, res_json)

    def test_only_silent(self):
        """Searching for silent should return only silent"""
        res_json = self.get_spots_for_noise_levels(['silent'])
        self.assertResponseSpaces(res_json, [self.silent_spot])

    def test_only_quiet(self):
        """Quiet should return...
           This test relied on UW-specific filters, and has been moved to
           test/search/uw_noise.py as test_uw_only_quiet(). This remains as a
           test stub for a test for generic filters.
        """
        pass

    def test_only_moderate(self):
        """Moderate should return...
           This test relied on UW-specific filters, and has been moved to
           test/search/uw_noise.py as test_uw_only_moderate(). This remains as
           a test stub for a test for generic filters.
        """
        pass

    def test_silent_and_quiet(self):
        """Silent+quiet should return...
           This test relied on UW-specific filters, and has been moved to
           test/search/uw_noise.py as test_uw_silent_and_quiet(). This remains
           as a test stub for a test for generic filters.
        """
        pass

    def test_silent_and_moderate(self):
        """Silent+moderate should return...
           This test relied on UW-specific filters, and has been moved to
           test/search/uw_noise.py as test_uw_silent_and_moderate(). This
           remains as a test stub for a test for generic filters.
        """
        pass

    def test_all_three(self):
        """All 3 should return...
           This test relied on UW-specific filters, and has been moved to
           test/search/uw_noise.py as test_uw_all_three(). This remains as a
           test stub for a test for generic filters.
        """
        pass
