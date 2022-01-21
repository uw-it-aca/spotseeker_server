# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.contrib.auth.models import User
from spotseeker_server.models import Spot, SpaceReview
import json


@override_settings(
    SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.fake_oauth",
    SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms."
    "spot.DefaultSpotForm",
)
class ReviewsTest(TestCase):
    def test_no_reviews(self):
        spot = Spot.objects.create(name="Test Review")

        c = Client()
        url = "/api/v1/spot/%s/reviews" % (spot.pk)

        response = c.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content.decode(), "[]")

    def test_submit_no_publish(self):
        spot = Spot.objects.create(name="Test Review")

        c = Client()
        url = "/api/v1/spot/%s/reviews" % (spot.pk)

        json_data = {
            "rating": 5,
            "review": "This space is great",
        }

        response = c.post(
            url,
            json.dumps(json_data),
            content_type="application/json",
            TESTING_OAUTH_USER="review",
        )
        self.assertEquals(response.status_code, 201)

        response = c.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content.decode(), "[]")

    @override_settings(SPOTSEEKER_AUTH_ADMINS=["is_admin"])
    def test_publishing(self):
        spot = Spot.objects.create(name="Test Review")

        c = self.client
        url = "/api/v1/spot/%s/reviews" % (spot.pk)

        json_data = {
            "rating": 5,
            "review": "This space is great",
        }

        response = c.post(
            url,
            json.dumps(json_data),
            content_type="application/json",
            TESTING_OAUTH_USER="review",
        )
        self.assertEquals(response.status_code, 201)

        response = c.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content.decode(), "[]")

        url = "/api/v1/reviews/unpublished"
        response = c.get(url, TESTING_OAUTH_USER="is_admin")
        reviews = json.loads(response.content)

        for review in reviews:
            if review["space_id"] == spot.pk:
                json_data = {
                    "review_id": review["id"],
                    "publish": True,
                    "review": "This is the edited review",
                }

                response = c.post(
                    url,
                    json.dumps(json_data),
                    content_type="application/json",
                    TESTING_OAUTH_USER="is_admin",
                )
                self.assertEquals(response.status_code, 200)
                self.assertEquals(response.content.decode(), "")

        url = "/api/v1/spot/%s/reviews" % (spot.pk)
        response = c.get(url)
        reviews = json.loads(response.content)
        self.assertEquals(len(reviews), 1)
        self.assertEquals(reviews[0]["review"], "This is the edited review")

        url = "/api/v1/spot/%s" % (spot.pk)
        response = c.get(url)

        spot_data = json.loads(response.content)
        self.assertEquals(spot_data["extended_info"]["rating"], "5.0")
        self.assertEquals(spot_data["extended_info"]["review_count"], "1")

    @override_settings(SPOTSEEKER_AUTH_ADMINS=["is_admin"])
    def test_deletion(self):
        c = self.client
        spot = Spot.objects.create(name="Test Review")
        user = User.objects.create_user("foo", "a@b.c", "pass")
        # Create a published review
        review = spot.spacereview_set.create(
            rating=5,
            review="foo",
            is_published=True,
            is_deleted=False,
            reviewer=user,
        )
        rev_url = "/api/v1/reviews/unpublished"
        spot_reviews_url = "/api/v1/spot/%s/reviews" % spot.pk
        # Assert the review shows up before we delete it
        response = c.get(spot_reviews_url)
        reviews_data = json.loads(response.content)
        self.assertEquals(len(reviews_data), 1)
        self.assertEquals(reviews_data[0]["review"], "foo")

        json_data = {
            "review_id": review.pk,
            "review": "foo",
            "delete": True,
            "publish": True,
        }
        response = c.post(
            rev_url,
            json.dumps(json_data),
            content_type="application/json",
            TESTING_OAUTH_USER="is_admin",
        )
        self.assertEquals(response.status_code, 200)
        # Assert that the review no longer shows up for the spot
        response = c.get(spot_reviews_url)
        reviews_data = json.loads(response.content)
        self.assertEquals(len(reviews_data), 0)

    @override_settings(SPOTSEEKER_AUTH_ADMINS=["is_admin"])
    def test_invalid_json(self):
        """Test Error handling behavior"""
        spot = Spot.objects.create(name="Test Review")
        url = "/api/v1/spot/%s/reviews" % (spot.pk)
        invalid_json = "{foo bar"
        response = self.client.post(
            url,
            invalid_json,
            content_type="application/json",
            TESTING_OAUTH_USER="review",
        )
        self.assertEquals(response.status_code, 400)
        self.assertIn("Unable to parse JSON", response.content.decode())

    @override_settings(SPOTSEEKER_AUTH_ADMINS=["is_admin"])
    def test_invalid_ratings(self):
        spot = Spot.objects.create(name="Test Review")

        c = Client()
        url = "/api/v1/spot/%s/reviews" % (spot.pk)

        json_data = {
            "rating": 6,
            "review": "This space is super great",
        }

        response = c.post(
            url,
            json.dumps(json_data),
            content_type="application/json",
            TESTING_OAUTH_USER="review",
        )
        self.assertEquals(response.status_code, 400)

        json_data = {
            "rating": 0,
            "review": "This space is super bad",
        }

        response = c.post(
            url,
            json.dumps(json_data),
            content_type="application/json",
            TESTING_OAUTH_USER="review",
        )
        self.assertEquals(response.status_code, 400)

        json_data = {
            "rating": -1,
            "review": "This space is super bad",
        }

        response = c.post(
            url,
            json.dumps(json_data),
            content_type="application/json",
            TESTING_OAUTH_USER="review",
        )
        self.assertEquals(response.status_code, 400)

        response = c.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content.decode(), "[]")

        url = "/api/v1/reviews/unpublished"
        response = c.get(url, TESTING_OAUTH_USER="is_admin")
        reviews = json.loads(response.content)

        total_reviews = 0
        for review in reviews:
            if review["space_id"] == spot.pk:
                total_reviews = total_reviews + 1

        self.assertEquals(total_reviews, 0)

    @override_settings(SPOTSEEKER_AUTH_ADMINS=["is_admin"])
    def test_publishing_multiple(self):
        spot = Spot.objects.create(name="Test Review")

        c = Client()
        url = "/api/v1/spot/%s/reviews" % (spot.pk)

        json_data = {
            "rating": 5,
            "review": "This space is great",
        }

        response = c.post(
            url,
            json.dumps(json_data),
            content_type="application/json",
            TESTING_OAUTH_USER="review",
        )
        self.assertEquals(response.status_code, 201)

        json_data = {
            "rating": 4,
            "review": "This space is good",
        }

        response = c.post(
            url,
            json.dumps(json_data),
            content_type="application/json",
            TESTING_OAUTH_USER="review",
        )
        self.assertEquals(response.status_code, 201)

        json_data = {
            "rating": 2,
            "review": "This space is bad",
        }

        response = c.post(
            url,
            json.dumps(json_data),
            content_type="application/json",
            TESTING_OAUTH_USER="review",
        )
        self.assertEquals(response.status_code, 201)

        response = c.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content.decode(), "[]")

        url = "/api/v1/reviews/unpublished"
        response = c.get(url, TESTING_OAUTH_USER="is_admin")
        reviews = json.loads(response.content)

        for review in reviews:
            if review["space_id"] == spot.pk:
                json_data = {
                    "review_id": review["id"],
                    "publish": True,
                    "review": review["original_review"],
                }

                response = c.post(
                    url,
                    json.dumps(json_data),
                    content_type="application/json",
                    TESTING_OAUTH_USER="is_admin",
                )
                self.assertEquals(response.status_code, 200)
                self.assertEquals(response.content.decode(), "")

        url = "/api/v1/spot/%s/reviews" % (spot.pk)
        response = c.get(url)
        reviews = json.loads(response.content)
        self.assertEquals(len(reviews), 3)

        url = "/api/v1/spot/%s" % (spot.pk)
        response = c.get(url)

        spot_data = json.loads(response.content)
        self.assertEquals(spot_data["extended_info"]["rating"], "3.5")
        self.assertEquals(spot_data["extended_info"]["review_count"], "3")

    @override_settings(SPOTSEEKER_AUTH_ADMINS=["is_admin"])
    def test_admin_ok(self):
        c = Client()
        url = "/api/v1/reviews/unpublished"

        response = c.get(url, TESTING_OAUTH_USER="is_admin")

        self.assertEquals(response.status_code, 200)

    @override_settings(SPOTSEEKER_AUTH_ADMINS=["is_admin"])
    def test_not_admin_ok(self):
        c = Client()
        url = "/api/v1/reviews/unpublished"

        response = c.get(url, TESTING_OAUTH_USER="not_is_admin")

        self.assertEquals(response.status_code, 401)
