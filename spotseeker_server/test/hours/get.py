from django.utils import unittest
from django.test.client import Client
from spotseeker_server.models import Spot, SpotAvailableHours
import simplejson as json

class SpotHoursGETTest(unittest.TestCase):
    def setUp(self):
        spot = Spot.objects.create ( name = "This spot has available hours" )
        hours1 = SpotAvailableHours.objects.create(spot = spot, day = "m", start_time="00:00", end_time="10:00")
        hours2 = SpotAvailableHours.objects.create(spot = spot, day = "m", start_time="11:00", end_time="14:00")
        hours3 = SpotAvailableHours.objects.create(spot = spot, day = "t", start_time="11:00", end_time="14:00")
        hours4 = SpotAvailableHours.objects.create(spot = spot, day = "w", start_time="11:00", end_time="14:00")
        hours5 = SpotAvailableHours.objects.create(spot = spot, day = "th", start_time="11:00", end_time="14:00")
        hours6 = SpotAvailableHours.objects.create(spot = spot, day = "f", start_time="11:00", end_time="14:00")
        # Saturday is intentionally missing
        hours8 = SpotAvailableHours.objects.create(spot = spot, day = "su", start_time="11:00", end_time="14:00")

        self.spot = spot

    def test_hours(self):
        c = Client()
        url = "/api/v1/spot/%s" % self.spot.pk
        response = c.get(url)
        spot_dict = json.loads(response.content)

        valid_data = {
            'm': [ [ "00:00", "10:00" ], [ "11:00", "14:00" ] ],
            't': [ [ "11:00", "14:00" ] ],
            'w': [ [ "11:00", "14:00" ] ],
            't': [ [ "11:00", "14:00" ] ],
            'f': [ [ "11:00", "14:00" ] ],
            'sa': [ ],
            'su': [ [ "11:00", "14:00" ] ],
        }

        available_hours = spot_dict["available_hours"]
        self.assertEquals(available_hours, valid_data, "Data from the web service matches the data for the spot")




