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

from spotseeker_server.views.rest_dispatch import RESTDispatch, JSONResponse
from spotseeker_server.require_auth import *
from spotseeker_server.models import Spot
from django.http import HttpResponse
from django.core.exceptions import FieldError


class BuildingListView(RESTDispatch):
    """ Performs actions on the list of buildings, at /api/v1/buildings.
    GET returns 200 with a list of buildings.
    """
    @app_auth_required
    def GET(self, request):
        spots = Spot.objects.all()
        for key, value in request.GET.items():
            if key.startswith('oauth_'):
                pass
            else:
                try:
                    spots = Spot.objects.filter(**{key: value})
                except FieldError:
                    # If a FieldError is thrown, the key is probably SpotExtendedInfo
                    spots = Spot.objects.filter(spotextendedinfo__key=key, spotextendedinfo__value=value)

        q = spots.values('building_name').distinct()

        buildings = [b['building_name'] for b in q]
        buildings.sort()
        return JSONResponse(buildings)
