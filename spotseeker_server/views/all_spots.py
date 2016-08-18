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

    sbutler1@illinois.edu: adapt to the new RESTDispatch framework.
"""

from spotseeker_server.views.rest_dispatch import RESTDispatch, JSONResponse
from spotseeker_server.forms.spot import SpotForm
from spotseeker_server.models import *
from django.http import HttpResponse
from spotseeker_server.require_auth import *
from spotseeker_server.cache.spot import SpotCache


class AllSpotsView(RESTDispatch):

    @app_auth_required
    def GET(self, request):
        spot_cache = SpotCache()
        spots = spot_cache.get_all_spots()
        return JSONResponse(spots)
