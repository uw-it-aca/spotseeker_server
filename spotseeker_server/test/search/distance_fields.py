from django.utils import unittest
from django.test.client import Client
from spotseeker_server.models import Spot
import simplejson as json

class SpotSearchDistanceFieldTest(unittest.TestCase):
    def test_distances(self):
        # Spots are in the atlantic to make them less likely to collide with actual spots
        center_lat = 31.000000
        center_long = -41.000000

        inner_top = Spot.objects.create( name = "Atlantic Location 1", latitude = 31.0000898315, longitude = -41.0 )
        inner_top.save()

        inner_top2 = Spot.objects.create( name = "Alternate name of AL1", latitude = 31.0000898315, longitude = -41.0 )
        inner_top2.save()

        mid_top = Spot.objects.create( name = "Atlantic Location 2", latitude =  30.0004491576, longitude = -40.0 )
        mid_top.save()

        response = c.get("/api/v1/spot", { 'center_latititude':center_lat, 'center_longitude':center_long, 'distance':12, 'name':'Atlantic' })
        self.assertEquals(response.status_code, 200, "Accepts the distance query")
        spots = json.loads(response.content)
        self.assertEquals(len(spots), 1, "Returns 1 spot")

        self.assertEquals(spots[0].id, inner_top.pk, "Found the inner Atlantic spot")
