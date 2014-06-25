""" Copyright 2014 UW Information Technology, University of Washington

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
from django.conf import settings
from django.test.client import Client
from django.test.utils import override_settings
from django.contrib.auth.models import User
from spotseeker_server.models import FavoriteSpot, Spot
from mock import patch
from spotseeker_server import models
from django.core import cache
import json

@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.fake_oauth',
                   SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm')
class FavoritesTest(TestCase):
    def test_no_favorites(self):
        user, created = User.objects.get_or_create(username="fav_test0")
        c = Client()
        c.login(username="fav_test0")
        url = "/api/v1/user/me/favorites"
        response = c.get(url, TESTING_OAUTH_USER="fav_test0")

        self.assertEquals(response.status_code, 200, "200 on empty")
        self.assertEquals(response.content, "[]", "Empty array")

    def test_one_favorite(self):
        user, created = User.objects.get_or_create(username="fav_test1")
        self.assertEquals(created, True)

        spot = Spot.objects.create(name="This is for testing Fav 1")

        fav = FavoriteSpot.objects.create(user = user, spot = spot)

        c = Client()
        c.login(username="fav_test1")
        url = "/api/v1/user/me/favorites"
        response = c.get(url, TESTING_OAUTH_USER="fav_test1")

        self.assertEquals(response.status_code, 200, "200 on one")

        favorites = json.loads(response.content)

        self.assertEquals(len(favorites), 1)

        self.assertEquals(favorites[0]['name'], "This is for testing Fav 1")
        spot.delete()

    def test_multi_favorite(self):
        user, created = User.objects.get_or_create(username="fav_test2")
        self.assertEquals(created, True)

        spot1 = Spot.objects.create(name="This is for testing Fav 2")
        spot2 = Spot.objects.create(name="This is for testing Fav 3")

        fav1 = FavoriteSpot.objects.create(user = user, spot = spot1)
        fav2 = FavoriteSpot.objects.create(user = user, spot = spot2)

        c = Client()
        c.login(username="fav_test2")
        url = "/api/v1/user/me/favorites"
        response = c.get(url, TESTING_OAUTH_USER="fav_test2")

        self.assertEquals(response.status_code, 200, "200 on multi")

        favorites = json.loads(response.content)

        self.assertEquals(len(favorites), 2)

        spot1.delete()
        spot2.delete()

    def test_put(self):
        user, created = User.objects.get_or_create(username="fav_test3")
        self.assertEquals(created, True)

        spot1 = Spot.objects.create(name="This is for testing Fav 4")
        spot2 = Spot.objects.create(name="This is for testing Fav 5")

        c = Client()
        c.login(username="fav_test3")
        url = "/api/v1/user/me/favorites"
        response = c.get(url, TESTING_OAUTH_USER="fav_test3")
        favorites = json.loads(response.content)
        self.assertEquals(len(favorites), 0, "No initial favorites")

        url = "/api/v1/user/me/favorite/%s" % spot1.pk
        response = c.put(url, "True", content_type="application/json", TESTING_OAUTH_USER="fav_test3")

        url = "/api/v1/user/me/favorites"
        response = c.get(url, TESTING_OAUTH_USER="fav_test3")
        favorites = json.loads(response.content)
        self.assertEquals(len(favorites), 1, "One favorite added")

        url = "/api/v1/user/me/favorite/%s" % spot1.pk
        response = c.put(url, "True", content_type="application/json", TESTING_OAUTH_USER="fav_test3")

        url = "/api/v1/user/me/favorites"
        response = c.get(url, TESTING_OAUTH_USER="fav_test3")
        favorites = json.loads(response.content)
        self.assertEquals(len(favorites), 1, "No double dipping")

        url = "/api/v1/user/me/favorite/%s" % spot2.pk
        response = c.put(url, "True", content_type="application/json", TESTING_OAUTH_USER="fav_test3")

        url = "/api/v1/user/me/favorites"
        response = c.get(url, TESTING_OAUTH_USER="fav_test3")
        favorites = json.loads(response.content)
        self.assertEquals(len(favorites), 2, "Both added")

        spot1.delete()
        spot2.delete()

    def test_delete(self):
        user, created = User.objects.get_or_create(username="fav_test4")
        self.assertEquals(created, True)

        spot1 = Spot.objects.create(name="This is for testing Fav 6")
        spot2 = Spot.objects.create(name="This is for testing Fav 7")

        c = Client()
        url = "/api/v1/user/me/favorite/%s" % spot1.pk
        response = c.put(url, "True", content_type="application/json", TESTING_OAUTH_USER="fav_test4")

        url = "/api/v1/user/me/favorite/%s" % spot2.pk
        response = c.put(url, "True", content_type="application/json", TESTING_OAUTH_USER="fav_test4")

        url = "/api/v1/user/me/favorites"
        response = c.get(url, TESTING_OAUTH_USER="fav_test4")
        favorites = json.loads(response.content)
        self.assertEquals(len(favorites), 2, "Both added")

        url = "/api/v1/user/me/favorite/%s" % spot1.pk
        response = c.delete(url, TESTING_OAUTH_USER="fav_test4")

        url = "/api/v1/user/me/favorites"
        response = c.get(url, TESTING_OAUTH_USER="fav_test4")
        favorites = json.loads(response.content)
        self.assertEquals(len(favorites), 1, "one removed")
        self.assertEquals(favorites[0]["name"], spot2.name)


        url = "/api/v1/user/me/favorite/%s" % spot2.pk
        response = c.delete(url, TESTING_OAUTH_USER="fav_test4")

        url = "/api/v1/user/me/favorites"
        response = c.get(url, TESTING_OAUTH_USER="fav_test4")
        favorites = json.loads(response.content)
        self.assertEquals(len(favorites), 0, "all gone")

        spot1.delete()
        spot2.delete()


    def test_single_get(self):
        user, created = User.objects.get_or_create(username="fav_test5")
        self.assertEquals(created, True)

        spot1 = Spot.objects.create(name="This is for testing Fav 8")
        spot2 = Spot.objects.create(name="This is for testing Fav 9")
        spot3 = Spot.objects.create(name="This is for testing Fav 10")

        c = Client()
        url = "/api/v1/user/me/favorites"
        response = c.get(url, TESTING_OAUTH_USER="fav_test5")
        favorites = json.loads(response.content)
        self.assertEquals(len(favorites), 0, "No initial favorites")

        url = "/api/v1/user/me/favorite/%s" % spot1.pk
        response = c.put(url, "True", content_type="application/json", TESTING_OAUTH_USER="fav_test5")

        url = "/api/v1/user/me/favorite/%s" % spot1.pk
        response = c.get(url, TESTING_OAUTH_USER="fav_test5")
        favorite = json.loads(response.content)
        self.assertEquals(favorite, True, "One favorite added")

        url = "/api/v1/user/me/favorite/%s" % spot2.pk
        response = c.get(url, TESTING_OAUTH_USER="fav_test5")
        favorite = json.loads(response.content)
        self.assertEquals(favorite, False, "Not a fav")


        url = "/api/v1/user/me/favorite/%s" % spot3.pk
        response = c.put(url, "True", content_type="application/json", TESTING_OAUTH_USER="fav_test5")

        url = "/api/v1/user/me/favorite/%s" % spot1.pk
        response = c.get(url, TESTING_OAUTH_USER="fav_test5")
        favorite = json.loads(response.content)
        self.assertEquals(favorite, True, "One favorite added")

        url = "/api/v1/user/me/favorite/%s" % spot2.pk
        response = c.get(url, TESTING_OAUTH_USER="fav_test5")
        favorite = json.loads(response.content)
        self.assertEquals(favorite, False, "Not a fav")

        url = "/api/v1/user/me/favorite/%s" % spot3.pk
        response = c.get(url, TESTING_OAUTH_USER="fav_test5")
        favorite = json.loads(response.content)
        self.assertEquals(favorite, True, "Another favorite added")

        spot1.delete()
        spot2.delete()
        spot3.delete()
