# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" Changes
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
    """Performs actions on the list of buildings, at /api/v1/buildings.
    GET returns 200 with a list of buildings.
    """

    # @app_auth_required
    def GET(self, request):
        chain = SearchFilterChain(request)
        search_view = SearchView()
        spots = SearchView.filter_on_request(
            search_view, request.GET, chain, request.META, "buildings"
        )

        buildings = sorted(set([s.building_name for s in spots]))
        return JSONResponse(buildings)
