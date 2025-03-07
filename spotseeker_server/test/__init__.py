# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from spotseeker_server.models import Spot


class SpotServerTestCase(TestCase):
    """
    Centralized test methods for general spotseeker-server test cases.
    """
    def json_to_spot_ids(self, json):
        """Get spot IDs from a dictionary"""
        self.assertIsSpotList(json)
        return [spot['id'] for spot in json]

    def assertIsSpotList(self, json):
        """
        Assert that a dictionary contains a list of spots, suitable
        for use with json_to_spot_ids().
        """
        self.assertIsInstance(json, list, 'Expected list of spots')
        for spot in json:
            self.assertIn('id', spot)

    def assertJsonHeader(self, response):
        """Assert that a response contains JSON content type header."""
        self.assertIn('Content-Type', response,
                      'Response had no Content-Type')
        self.assertEqual(response['Content-Type'],
                         'application/json',
                         'Response had wrong Content-Type')

    @staticmethod
    def spot_sort_func(spot):
        """Sort func for a list of spots"""
        return spot['id']

    def assertSpotsToJson(self, spots, json, msg=None):
        """
        Compare some spot instances to json, using each spot's
        json_data_structure()
        """
        self.assertIsSpotList(json)

        # Expected
        exp_js = [spot.json_data_structure() for spot in spots]
        exp_js.sort(key=self.spot_sort_func)
        # Actual
        act_js = sorted(json, key=self.spot_sort_func)

        self.assertEqual(exp_js, act_js, msg)

    @classmethod
    def tearDownClass(cls):
        """Clean up all created spots when the test case is done"""
        Spot.objects.all().delete()

    # Defining these as static so they can be used in a setUpClass
    @staticmethod
    def new_spot(name, *args, **kwargs):
        """
        Create a new spot. First positional argument is used as the name,
        everything else is passed as-is to Spot.objects.create.
        """
        return Spot.objects.create(*args, name=name, **kwargs)

    @staticmethod
    def add_ei_to_spot(spot, **kv_pairs):
        """
        Add EI to a spot according to k/v pairs supplied in kwargs.
        Example:
        >>> spot = Spot.objects.create(name='Foo')
        >>> add_ei_to_spot(spot, campus='seattle', app_type='food')
        """
        for k, v in kv_pairs.items():
            spot.spotextendedinfo_set.create(key=k, value=v)
