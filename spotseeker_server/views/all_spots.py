# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" Changes
    =================================================================

    sbutler1@illinois.edu: adapt to the new RESTDispatch framework.
"""

from spotseeker_server.views.rest_dispatch import RESTDispatch, JSONResponse
from spotseeker_server.models import Spot
from spotseeker_server.require_auth import app_auth_required


class AllSpotsView(RESTDispatch):
    @app_auth_required
    def GET(self, request):
        spots = [spot.json_data_structure() for spot in Spot.objects.all()]
        return JSONResponse(spots)
