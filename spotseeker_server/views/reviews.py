# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from spotseeker_server.views.rest_dispatch import (
    RESTDispatch,
    RESTException,
    JSONResponse,
)
from spotseeker_server.models import Spot, SpaceReview
from spotseeker_server.require_auth import (
    user_auth_required,
    app_auth_required,
    admin_auth_required,
)
from django.http import HttpResponse
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
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

        rating = json_values["rating"]
        review = json_values["review"]

        if rating > 5 or rating < 1:
            return HttpResponse(status=400)

        new_review = space.spacereview_set.create(
            reviewer=user,
            original_review=review,
            rating=rating,
            is_published=False,
            is_deleted=False,
        )

        response = HttpResponse("OK", status=201)
        return response

    @app_auth_required
    def GET(self, request, spot_id, include_unpublished=False):
        space = Spot.objects.get(pk=spot_id)
        # Use the param after validating the user should see unpublished
        # reviews
        objects = space.spacereview_set.filter(is_published=True).order_by(
            "-date_submitted"
        )

        # seems to be a bug in sqlite3's handling of False booleans?
        reviews = [
            review.json_data_structure()
            for review in objects
            if not review.is_deleted
        ]

        return JSONResponse(reviews)


class UnpublishedReviewsView(RESTDispatch):
    @user_auth_required
    @admin_auth_required
    def GET(self, request):
        objects = SpaceReview.objects.filter(
            is_published=False, is_deleted=False
        )
        reviews = [review.full_json_data_structure() for review in objects]

        return JSONResponse(reviews)

    @user_auth_required
    @admin_auth_required
    def POST(self, request):
        data = json.loads(request.body)
        user = self._get_user(request)

        review = SpaceReview.objects.get(id=data["review_id"])
        review.review = data["review"]
        review.published_by = user
        if data["publish"]:
            review.date_published = timezone.now()

        review.is_published = data["publish"]
        if "delete" in data:
            review.is_deleted = data["delete"]

        review.save()
        review.space.update_rating()
        return JSONResponse("")
