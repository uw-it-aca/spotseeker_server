from django.test import TestCase
from django.core.cache import cache
from spotseeker_server.models import Spot


class SpotCacheTest(TestCase):

    def test_spot_caching(self):

        spot = Spot.objects.create(name='foo')
        spot_id = spot.pk

        js = spot.json_data_structure()
        cached_js = cache.get(spot_id)

        self.assertEqual(js, cached_js)

        spot.save()

        self.assertFalse(cache.has_key(spot_id))
        new_js = spot.json_data_structure()
        self.assertNotEqual(js['etag'], new_js['etag'])
        self.assertEqual(new_js['etag'], spot.etag)

        new_cached_js = cache.get(spot_id)
        self.assertEqual(new_js, new_cached_js)

        spot.delete()
        self.assertFalse(cache.has_key(spot_id))
