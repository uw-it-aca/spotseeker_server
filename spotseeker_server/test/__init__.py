from django.test import TestCase
from spotseeker_server.models import Spot

class SpotServerTestCase(TestCase):


    def json_to_spot_ids(self, json):
        self.assertIsSpotList(json)
        return [spot['id'] for spot in json]

    def assertIsSpotList(self, json):
        self.assertIsInstance(json, list, 'Expected list of spots')
        for spot in json:
            self.assertIn('id', spot)

    def assertJsonHeader(self, response):

        self.assertIn('Content-Type', response,
                      'Response had no Content-Type')
        self.assertEqual(response['Content-Type'],
                         'application/json',
                         'Response had wrong Content-Type')

    @staticmethod
    def spot_sort_func(spot):
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
    def tearDownClass(self):
        Spot.objects.all().delete()

    # Defining these as static so they can be used in a setUpClass
    @staticmethod
    def new_spot(name, *args, **kwargs):
        return Spot.objects.create(*args, name=name, **kwargs)

    @staticmethod
    def add_ei_to_spot(spot, **kv_pairs):
        for k, v in kv_pairs.items():
            spot.spotextendedinfo_set.create(key=k, value=v)
