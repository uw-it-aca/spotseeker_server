# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.test.client import Client
from spotseeker_server.models import Spot
import simplejson as json
from django.test.utils import override_settings
from mock import patch
from spotseeker_server import models


@override_settings(SPOTSEEKER_AUTH_MODULE="spotseeker_server.auth.all_ok")
class SpotSearchLimitTest(TestCase):
    def setUp(self):
        num_spots = 25
        self.num_spots = num_spots
        for i in range(num_spots):
            i = i + 1
            Spot.objects.create(name="spot %s" % (i))

    def test_more_than_20_no_limit(self):
        c = Client()
        get_request = "/api/v1/spot?"
        num_spots = self.num_spots

        for i in Spot.objects.all():
            get_request = get_request + "id=%s&" % (i.id)

        response = c.get(get_request)
        self.assertEquals(
            response.status_code,
            400,
            (
                "400 is thrown if more than 20 spots "
                "are requested without a limit"
            ),
        )

    def test_less_than_20_no_limit(self):
        c = Client()
        get_request = "/api/v1/spot?"
        num_spots = self.num_spots - 10

        for i in range(num_spots):
            i = i + 1
            get_request = get_request + "id=%s&" % (Spot.objects.all()[i].id)

        response = c.get(get_request)
        spots = json.loads(response.content)
        self.assertEquals(
            len(spots),
            num_spots,
            (
                "Spots requested were returned if "
                "less than 20 spots are requested without a limit"
            ),
        )

    def test_more_than_20_with_limit(self):
        c = Client()
        get_request = "/api/v1/spot?"
        num_spots = self.num_spots

        for i in Spot.objects.all():
            get_request = get_request + "id=%s&" % (i.id)
        get_request = get_request + "limit=%d" % (num_spots)

        response = c.get(get_request)
        spots = json.loads(response.content)
        self.assertEquals(
            len(spots),
            num_spots,
            (
                "Spots requested were returned even though "
                "more than 20 because a limit was included"
            ),
        )
