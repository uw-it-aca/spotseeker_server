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
from spotseeker_server.test import utils_test, ServerTest
from spotseeker_server.cache import memory_cache
from django.utils.unittest import skipUnless
from django.test.utils import override_settings
from spotseeker_server.models import Spot
from django.conf import settings
from spotseeker_server.cache.spot import SpotCache
from spotseeker_server.cache import memory_cache
import mock
import json


@override_settings(
    SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
    SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.'
                         'DefaultSpotForm',
    SPOTSEEKER_SPOTEXTENDEDINFO_FORM='spotseeker_server.default_forms.spot.'
                                     'DefaultSpotExtendedInfoForm',
    SPOTSEEKER_AUTH_ADMINS=('demo_user',))
@mock.patch.object(SpotCache, 'implementation',
                   return_value=memory_cache)
class MemoryCacheTest(ServerTest):
    """This class should test that the cache functionality works as intended"""
    def test_spot_caches(self, _):
        """Test that once POSTed, a spot will save to the cache"""
        spot = utils_test.get_spot('Spot Name', 20)
        response = self.client.post('/api/v1/spot/', json.dumps(spot),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 201)

        self.assertIn(1, memory_cache.spots_cache.keys())
        spot_model = Spot.objects.get(id=1)

        self.assertEqual(memory_cache.spots_cache[1],
                         spot_model.json_data_structure())

    def test_get_spot_not_in_cache(self, _):
        """
        Tests that retrieving a spot not in the cache will return the spot.
        """
        spot = Spot.objects.create(name="Hi!")

        from_cache = memory_cache.get_spot(spot)

        self.assertEquals(spot.json_data_structure(), from_cache,
                          "The cached and DB data should be the same!")

    def test_get_all_spots(self, _):
        """Test get_all_spots"""
        spot = Spot.objects.create(name="Bye!")
        memory_cache.load_spots()

        cached_spots = memory_cache.get_all_spots()
        self.assertEqual(len(cached_spots), 1)
        cached = cached_spots[0]
        self.assertEqual(spot.name, cached['name'])

    def test_spot_update(self, _):

        old_bldg = 'Small Building'
        new_bldg = 'Big Building'

        spot = Spot.objects.create(name='Foo',
                                   building_name=old_bldg)
        spot_id = spot.id
        memory_cache.load_spots()

        old_spot_dict = memory_cache.get_spot(spot)
        old_etag = old_spot_dict['etag']

        spot.building_name = new_bldg
        spot.save()

        new_spot_dict = memory_cache.get_spot(spot)
        new_etag = new_spot_dict['etag']

        self.assertNotEqual(old_etag, new_etag, 'Spot etag did not change')
        self.assertEqual(new_spot_dict['location']['building_name'], new_bldg)
