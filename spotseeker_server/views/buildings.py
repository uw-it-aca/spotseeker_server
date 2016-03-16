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

    Changes
    =================================================================

    sbutler1@illinois.edu: adapt to the new RESTDispatch framework;
        remove needless use of regex.
"""

from spotseeker_server.views.rest_dispatch import RESTDispatch, JSONResponse
from spotseeker_server.require_auth import *
from spotseeker_server.models import Spot
from spotseeker_server.org_filters import SearchFilterChain
from spotseeker_server.views.search import SearchView
from django.http import HttpResponse
from django.core.exceptions import FieldError


class BuildingListView(RESTDispatch):
    """ Performs actions on the list of buildings, at /api/v1/buildings.
    GET returns 200 with a list of buildings.
    """
    @app_auth_required
    def GET(self, request):
        chain = SearchFilterChain(request)
        search_view = SearchView()
        spots = SearchView.filter_on_request(search_view,
                                             request.GET,
                                             chain,
                                             request.META,
                                             'buildings')

        buildings = []
        for spot in spots:
            if spot.building_name not in buildings:
                buildings.append(spot.building_name)

        buildings.sort()
        return JSONResponse(buildings)
