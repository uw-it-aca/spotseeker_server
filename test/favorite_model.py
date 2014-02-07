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

from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User
from spotseeker_server import models
from mock import patch
from django.core import cache

@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                   SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm')
class FavoriteSpotTest(TestCase):

    def setUp(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            #create user
            self.user = User.objects.create_user('favoriter', 'nobody@nowhere.net', 'password')
            self.user.save()
            # create spot
            self.spot = models.Spot.objects.create(name="This is for testing Favorites", latitude=55, longitude=30)
            self.spot.save()
            #create favorite and assign to user
            self.fav1 = models.FavoriteSpot.objects.create(user=self.user, spot=self.spot)
            self.fav1.save()

    def test_json(self):
        """ FavoriteSpots should return JSON for the Spot that was fovorited.
        """
        pass

    def test_user_and_spot(self):
        """You should be able to get a favorited spot's JSON via the user that favorited it.
        """
        self.assertEqual(self.fav1.user, self.user, "The user is the same when retrieved from the Favorite")
        self.assertEqual(self.fav1.spot, self.spot, "The spot is the same when retrieved from the Favorite")
