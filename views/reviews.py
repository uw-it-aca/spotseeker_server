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

from spotseeker_server.views.rest_dispatch import RESTDispatch, RESTException, JSONResponse
from spotseeker_server.models import Spot, SpaceReview
from spotseeker_server.require_auth import user_auth_required, app_auth_required
from django.http import HttpResponse

class ReviewsView(RESTDispatch):
    @user_auth_required
    def POST(self, request, spot_id):
        response = HttpResponse("OK")
        return response

    @app_auth_required
    def GET(self, request, spot_id, include_unpublished=False):
        space = Spot.objects.get(pk=spot_id)

        # Use the param after validating the user should see unpublished
        # reviews

        reviews = []
        objects = SpaceReview.objects.filter(space=space, is_published=True)

        for review in objects:
            reviews.append(review.json_data_structure())

        return JSONResponse(reviews)
