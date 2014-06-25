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

from spotseeker_server.views.rest_dispatch import RESTDispatch, JSONResponse
from spotseeker_server.require_auth import user_auth_required
from spotseeker_server.models import Spot, FavoriteSpot
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
import logging

logger = logging.getLogger(__name__)

class FavoritesView(RESTDispatch):
    """ Performs actions on the user's favorites, at /api/v1/user/me/favorites.
    GET returns 200 with a list of spots.
    """
    @user_auth_required
    @never_cache
    def GET(self, request, spot_id = None):
        if spot_id is None:
            return self._get_all_favorites(request)
        else:
            return self._get_is_favorite(request, spot_id)

    @user_auth_required
    def PUT(self, request, spot_id):
        user = self._get_user(request)
        spot = Spot.objects.get(pk=spot_id)

        log_message = "user: %s; spot_id: %s; favorite added" % (user.username, spot.pk)
        logger.info(log_message)
        fav, created = FavoriteSpot.objects.get_or_create(user=user, spot=spot)
        return JSONResponse(True)

    @user_auth_required
    def DELETE(self, request, spot_id):
        user = self._get_user(request)
        spot = Spot.objects.get(pk=spot_id)

        fav = FavoriteSpot.objects.filter(user=user, spot=spot)
        for obj in fav:
            fav.delete()

        log_message = "user: %s; spot_id: %s; favorite removed" % (user.username, spot.pk)
        logger.info(log_message)
        return JSONResponse("")

    def _get_all_favorites(self, request):
        user = self._get_user(request)
        favorites = []

        objects = FavoriteSpot.objects.filter(user = user)

        for fav in objects:
            if hasattr(fav, 'spot'):
                json = fav.spot.json_data_structure()
                favorites.append(fav.spot.json_data_structure())

        return JSONResponse(favorites)

    def _get_is_favorite(self, request, spot_id):
        user = self._get_user(request)
        spot = Spot.objects.get(pk=spot_id)

        fav = FavoriteSpot.objects.filter(user=user, spot=spot)
        if len(fav):
            return JSONResponse(True)
        return JSONResponse(False)
