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
    """ Tests the FavoriteSpot model.
    """

    def setUp(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            # create user
            self.user = User.objects.create_user('favoriter', 'nobody@nowhere.net', 'password')
            self.user.save()
            # create spots
            self.spot = models.Spot.objects.create(name="This is for testing Favorites", latitude=55, longitude=30)
            self.spot.save()
            self.spot2 = models.Spot.objects.create(name="This is for testing multiple Favorites", latitude=56, longitude=56)
            self.spot2.save()
            # create favorite and assign to user
            self.fav1 = models.FavoriteSpot.objects.create(user=self.user, spot=self.spot)
            self.fav1.save()
            self.fav2 = models.FavoriteSpot.objects.create(user=self.user, spot=self.spot2)
            self.fav2.save()

    def tearDown(self):
        self.user.delete()
        self.spot.delete()
        self.spot2.delete()
        self.fav1.delete()
        self.fav2.delete()

    def test_json(self):
        """ FavoriteSpots should return JSON for the Spot that was fovorited.
        """
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            # get JSON from FavoriteSpot
            fav1_json = self.fav1.json_data_structure()
            # get JSON from Spot
            spot_json = self.spot.json_data_structure()
            # compare
            self.assertEqual(spot_json, fav1_json, "The same JSON is returned by both the Spot and the FavoriteSpot")

            # get JSON from FavoriteSpot via User
            fav1 = self.user.favoritespot_set.get(pk=self.fav1.pk)
            fav1_json = fav1.json_data_structure()
            # get JSON from Spot
            spot_json = self.spot.json_data_structure()
            # compare
            self.assertEqual(spot_json, fav1_json, "The same JSON is returned by both the Spot and the FavoriteSpot")

    def test_user_and_spot(self):
        dummy_cache = cache.get_cache('django.core.cache.backends.dummy.DummyCache')
        with patch.object(models, 'cache', dummy_cache):
            # make sure a user can have multiple FavoriteSpots, but not to the same Spot
            queryset = self.user.favoritespot_set.all()
            orig_favs = list(queryset)
            fav3 = models.FavoriteSpot.objects.create(user=self.user, spot=self.spot)
            fav3.save()
            new_favs = list(queryset)
            self.assertEqual(orig_favs, new_favs, "There are no duplicate favorites")
