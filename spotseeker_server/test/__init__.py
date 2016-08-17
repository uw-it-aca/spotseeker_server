from django.test import TestCase
from spotseeker_server.cache.spot import SpotCache


class ServerTest(TestCase):

    clear_mem_cache = True

    def setUp(self):
        if self.clear_mem_cache:
            spot_cache = SpotCache()
            spot_cache.clear_cache()

    def tearDown(self):
        spot_cache = SpotCache()
        spot_cache.clear_cache()
