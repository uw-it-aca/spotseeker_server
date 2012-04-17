from django.utils import unittest
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot, SpotAvailableHours
import simplejson as json
from datetime import datetime
import datetime as alternate_date

from time import *

class SpotHoursOpenNowTest(unittest.TestCase):
    settings.SPOTSEEKER_AUTH_MODULE = 'spotseeker_server.auth.all_ok';
    def test_open_now(self):
        open_spot = Spot.objects.create ( name = "This spot is open now" )
        no_hours_spot = Spot.objects.create( name = "This spot has no hours" )
        closed_spot = Spot.objects.create ( name = "This spot has hours, but is closed" )

        now = datetime.time(datetime.now())

        open_start = alternate_date.time(now.hour - 1, now.minute)
        open_end   = alternate_date.time(now.hour + 1, now.minute)

        closed_start = alternate_date.time(now.hour + 1, now.minute)
        closed_end   = alternate_date.time(now.hour + 2, now.minute)

        day_lookup = ["su", "m", "t", "w", "th", "f", "sa"]
        day_num = int(strftime("%w", localtime()))
        today = day_lookup[day_num]

        open_hours = SpotAvailableHours.objects.create(spot = open_spot, day = today, start_time = open_start, end_time = open_end)
        closed_hours = SpotAvailableHours.objects.create(spot = closed_spot, day = today, start_time = closed_start, end_time = closed_end)

        # Testing to make sure too small of a radius returns nothing
        c = Client()
        response = c.get("/api/v1/spot", { 'open_now': True })
        self.assertEquals(response.status_code, 200, "Accepts a query for open now")
        spots = json.loads(response.content)

        has_open_spot = False
        has_closed_spot = False
        has_no_hours_spot = False

        for spot in spots:
            if spot['id'] == open_spot.pk:
                has_open_spot = True

            if spot['id'] == closed_spot.pk:
                has_closed_spot = True

            if spot['id'] == no_hours_spot.pk:
                has_no_hours_spot = True

        self.assertEquals(has_closed_spot, False, "Doesn't find the closed spot")
        self.assertEquals(has_no_hours_spot, False, "Doesn't find the spot with no hours")
        self.assertEquals(has_open_spot, True, "Finds the open spot")

