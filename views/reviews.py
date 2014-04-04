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
from spotseeker_server.require_auth import user_auth_required, app_auth_required, admin_auth_required
from django.http import HttpResponse
from datetime import datetime
import json

class ReviewsView(RESTDispatch):
    @user_auth_required
    def POST(self, request, spot_id):
        user = self._get_user(request)
        space = Spot.objects.get(pk=spot_id)

        body = request.read()
        try:
            json_values = json.loads(body)
        except Exception as e:
            raise RESTException("Unable to parse JSON", status_code=400)

        rating = json_values['rating']
        review = json_values['review']

        new_review = SpaceReview.objects.create(space = space,
                                                reviewer = user,
                                                original_review = review,
                                                rating = rating,
                                                is_published = False,
                                                is_deleted = False)

        response = HttpResponse("OK")
        return response

    @app_auth_required
    def GET(self, request, spot_id, include_unpublished=False):
        space = Spot.objects.get(pk=spot_id)

        # Use the param after validating the user should see unpublished
        # reviews

        reviews = []
        objects = SpaceReview.objects.filter(space=space, is_published=True, is_deleted=False)

        for review in objects:
            reviews.append(review.json_data_structure())

        return JSONResponse(reviews)

class UnpublishedReviewsView(RESTDispatch):
    @user_auth_required
    @admin_auth_required
    def GET(self, request):
        reviews = []
        objects = SpaceReview.objects.filter(is_published=False, is_deleted=False)

        for review in objects:
            reviews.append(review.full_json_data_structure())

        return JSONResponse(reviews)

    @user_auth_required
    @admin_auth_required
    def POST(self, request):
        data = json.loads(request.body)

        review = SpaceReview.objects.get(id=data["review_id"])
        review.review = data['review']
        review.published_by = request.user
        if data['publish']:
            review.date_published = datetime.now()

        review.is_published = data['publish']
        review.is_deleted = data['delete']

        review.save()
        review.space.update_rating()

        return JSONResponse('')

