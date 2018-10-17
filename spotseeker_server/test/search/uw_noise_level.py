from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
import simplejson as json
from spotseeker_server.models import Spot, SpotExtendedInfo
from spotseeker_server.org_filters import SearchFilterChain


def spot_with_noise_level(name, noise_level):
    """Create a spot with the given noise level"""
    spot = Spot.objects.create(name=name)
    spot.spotextendedinfo_set.create(key='noise_level',
                                     value=noise_level)
    return spot


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                   SPOTSEEKER_SEARCH_FILTERS=(
                       'spotseeker_server.org_filters.uw_search.Filter',))
class UWNoiseLevelTestCase(TestCase):

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
        SearchFilterChain._load_filters()  # make sure the uw filters is loaded
        res_json = self.get_spots_for_noise_levels(['silent'])
        self.assertResponseSpaces(res_json, [self.silent_spot])

    def test_uw_only_quiet(self):
        """Quiet should return both a quiet spot and variable"""
        SearchFilterChain._load_filters()  # make sure the uw filters is loaded
        res_json = self.get_spots_for_noise_levels(['quiet'])
        expected = [self.quiet_spot, self.variable_spot]
        self.assertResponseSpaces(res_json, expected)

    def test_uw_only_moderate(self):
        """Moderate should return moderate and variable"""
        SearchFilterChain._load_filters()  # make sure the uw filters is loaded
        res_json = self.get_spots_for_noise_levels(['moderate'])
        expected = [self.moderate_spot, self.variable_spot]
        self.assertResponseSpaces(res_json, expected)

    def test_uw_silent_and_quiet(self):
        """Silent+quiet should give everything but moderate"""
        SearchFilterChain._load_filters()  # make sure the uw filters is loaded
        res_json = self.get_spots_for_noise_levels(['silent', 'quiet'])
        expected = [self.quiet_spot, self.silent_spot, self.variable_spot]
        self.assertResponseSpaces(res_json, expected)

    def test_uw_silent_and_moderate(self):
        """Silent+moderate should give everything but quiet"""
        SearchFilterChain._load_filters()  # make sure the uw filters is loaded
        res_json = self.get_spots_for_noise_levels(['silent', 'moderate'])
        expected = [self.silent_spot, self.moderate_spot, self.variable_spot]
        self.assertResponseSpaces(res_json, expected)

    def test_uw_all_three(self):
        """All 3 should give everything"""
        SearchFilterChain._load_filters()  # make sure the uw filters is loaded
        query = ['silent', 'quiet', 'moderate']
        res_json = self.get_spots_for_noise_levels(query)
        expected = [self.silent_spot,
                    self.quiet_spot,
                    self.moderate_spot,
                    self.variable_spot]
        self.assertResponseSpaces(res_json, expected)
