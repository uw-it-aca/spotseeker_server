from django.test import TestCase
from spotseeker_server.cache import memory_cache


class ServerTest(TestCase):

    clear_mem_cache = True

    def setUp(self):
        if self.clear_mem_cache:
            memory_cache.clear_cache()

    def tearDown(self):
        memory_cache.clear_cache()
