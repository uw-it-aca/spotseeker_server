from spotseeker_server.test import utils_test, ServerTest
from spotseeker_server.cache import memory_cache
from django.test.utils import override_settings
from spotseeker_server.models import Spot
import json


@override_settings(
    SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
    SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.'
                         'DefaultSpotForm',
    SPOTSEEKER_SPOTEXTENDEDINFO_FORM='spotseeker_server.default_forms.spot.'
                                     'DefaultSpotExtendedInfoForm',
    SPOTSEEKER_AUTH_ADMINS=('demo_user',))
class MemoryCacheTest(ServerTest):
    """This class should test that the cache functionality works as intended"""
    def test_spot_caches(self):
        """Test that once POSTed, a spot will save to the cache"""
        spot = utils_test.get_spot('Spot Name', 20)
        response = self.client.post('/api/v1/spot/', json.dumps(spot),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 201)

        self.assertIn(1, memory_cache.spots_cache.keys())
        spot_model = Spot.objects.get(id=1)

        self.assertEqual(memory_cache.spots_cache[1],
                         spot_model.json_data_structure())

    def test_get_spot_not_in_cache(self):
        """
        Tests that retrieving a spot not in the cache will return the spot.
        """
        spot = Spot.objects.create(name="Hi!")

        from_cache = memory_cache.get_spot(spot)

        self.assertEquals(spot.json_data_structure(), from_cache,
                          "The cached and DB data should be the same!")
