# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase, override_settings
from django.core.cache import cache
from spotseeker_server.models import Spot


class SpotCacheTest(TestCase):

    @override_settings(CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    })
    def test_spot_caching(self):

        spot = Spot.objects.create(name='foo')
        spot_id = spot.pk

        # Assert that a cache entry is created when we call
        # json_data_structure()
        js = spot.json_data_structure()
        cached_js = cache.get(spot.json_cache_key())
        self.assertEqual(js, cached_js)

        # Assert that saving the spot removes the cache entry
        spot.save()
        self.assertNotIn(spot_id, cache)

        # Assert that the spot now has a new etag
        new_js = spot.json_data_structure()
        self.assertNotEqual(js['etag'], new_js['etag'])
        self.assertEqual(new_js['etag'], spot.etag)

        # Assert the new cache entry reflects the updated etag
        new_cached_js = cache.get(spot.json_cache_key())
        self.assertEqual(new_js, new_cached_js)

        # Assert that deleting the spot removes the cache entry
        spot.delete()
        self.assertNotIn(spot_id, cache)
