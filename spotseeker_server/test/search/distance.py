from django.utils import unittest
from django.test.client import Client
from spotseeker_server.models import Spot
import simplejson as json

class SpotSearchDistanceTest(unittest.TestCase):
    def test_distances(self):


    

        # Spots are in the atlantic to make them less likely to collide with actual spots
        center_lat = 30.000000
        center_long = -40.000000

        # Inner spots are 10 meters away from the center
        # Mid spots are 50 meters away from the center
        # Outer spots are 100 meters away from the center
        # Far out spots are 120 meters away, at the north
        inner_top = Spot.objects.create( name = "Inner Top", latitude = 30.0000898315, longitude = -40.0 )
        inner_top.save()
        inner_bottom = Spot.objects.create( name = "Inner Bottom", latitude = 29.9999101685, longitude = -40.0 )
        inner_bottom.save()
        inner_left = Spot.objects.create( name = "Inner Left", latitude = 30.0, longitude = -40.0001037285)
        inner_left.save()
        inner_right = Spot.objects.create( name = "Inner Right", latitude = 30.0, longitude = -39.9998962715 )
        inner_right.save()

        mid_top = Spot.objects.create( name = "Mid Top", latitude =  30.0004491576, longitude = -40.0 )
        mid_top.save()
        mid_bottom = Spot.objects.create( name = "Mid Bottom", latitude = 29.9995508424, longitude = -40.0 )
        mid_bottom.save()
        mid_left = Spot.objects.create( name = "Mid Left", latitude = 30.0, longitude = -40.0005186426 )
        mid_left.save()
        mid_right = Spot.objects.create( name = "Mid Right", latitude = 30.0, longitude = -39.9994813574 )
        mid_right.save()

        outer_top = Spot.objects.create( name = "Outer Top", latitude = 30.0008983153, longitude = -40.0 )
        outer_top.save()
        outer_bottom = Spot.objects.create( name = "Outer Bottom", latitude = 29.9991016847, longitude = -40.0 )
        outer_bottom.save()
        outer_left = Spot.objects.create( name = "Outer Left", latitude = 30.0, longitude = -40.0010372851 )
        outer_left.save()
        outer_right = Spot.objects.create( name = "Outer Right", latitude = 30.0, longitude = -39.9989627149 )
        outer_right.save()

        for i in range(0, 100):
            far_out = Spot.objects.create( name = "Far Out %s" % i, latitude = 30.0010779783 , longitude = 40.0)
            far_out.save()


        # Testing to make sure too small of a radius returns nothing
        c = Client()
        response = c.get("/api/v1/spot", { 'center_latititude':center_lat, 'center_longitude':center_long, 'distance':1 })
        self.assertEquals(response.status_code, 200, "Accepts a query with no matches")
        self.assertEquals(response.content, '[]', "Should return no matches")

        # Testing the inner ring
        response = c.get("/api/v1/spot", { 'center_latititude':center_lat, 'center_longitude':center_long, 'distance':12 })
        self.assertEquals(response.status_code, 200, "Accepts the distance query")
        spots = json.loads(response.content)
        self.assertEquals(len(spots), 4, "Returns 4 spots")
        spot_ids = {
            inner_left.pk : 1,
            inner_right.pk : 1,
            inner_top.pk : 1,
            inner_bottom.pk : 1,
        }
        for spot in spots:
            self.assertEquals(spot_ids[spot.pk], 1, "Spot matches a unique inner spot")
            spot_ids[spot.pk] = 2

        # Testing the mid ring
        response = c.get("/api/v1/spot", { 'center_latititude':center_lat, 'center_longitude':center_long, 'distance':60 })
        self.assertEquals(response.status_code, 200, "Accepts the distance query")
        spots = json.loads(response.content)
        self.assertEquals(len(spots), 8, "Returns 8 spots")
        spot_ids = {
            inner_left.pk : 1,
            inner_right.pk : 1,
            inner_top.pk : 1,
            inner_bottom.pk : 1,
            mid_left.pk : 1,
            mid_right.pk : 1,
            mid_top.pk : 1,
            mid_bottom.pk : 1,
        }
        for spot in spots:
            self.assertEquals(spot_ids[spot.pk], 1, "Spot matches a unique inner or mid spot")
            spot_ids[spot.pk] = 2


        # Testing the outer ring
        response = c.get("/api/v1/spot", { 'center_latititude':center_lat, 'center_longitude':center_long, 'distance':110 })
        self.assertEquals(response.status_code, 200, "Accepts the distance query")
        spots = json.loads(response.content)
        self.assertEquals(len(spots), 12, "Returns 12 spots")
        spot_ids = {
            inner_left.pk : 1,
            inner_right.pk : 1,
            inner_top.pk : 1,
            inner_bottom.pk : 1,
            mid_left.pk : 1,
            mid_right.pk : 1,
            mid_top.pk : 1,
            mid_bottom.pk : 1,
            outer_left.pk : 1,
            outer_right.pk : 1,
            outer_top.pk : 1,
            outer_bottom.pk : 1,
        }
        for spot in spots:
            self.assertEquals(spot_ids[spot.pk], 1, "Spot matches a unique inner, mid or outer spot")
            spot_ids[spot.pk] = 2

        # testing a limit - should get the inner 4, and any 2 of the mid
        response = c.get("/api/v1/spot", { 'center_latititude':center_lat, 'center_longitude':center_long, 'distance':60 ,'limit':6})
        self.assertEquals(response.status_code, 200, "Accepts the distance query")
        spots = json.loads(response.content)
        self.assertEquals(len(spots), 6, "Returns 6 spots")
        spot_ids = {
            inner_left.pk : 1,
            inner_right.pk : 1,
            inner_top.pk : 1,
            inner_bottom.pk : 1,
            mid_left.pk : 1,
            mid_right.pk : 1,
            mid_top.pk : 1,
            mid_bottom.pk : 1,
        }
        for spot in spots:
            self.assertEquals(spot_ids[spot.pk], 1, "Spot matches a unique inner, mid or outer spot")
            spot_ids[spot.pk] = 2


        self.assertEquals(spot_ids[inner_left.pk], 2, "Inner left was selected")
        self.assertEquals(spot_ids[inner_right.pk], 2, "Inner right was selected")
        self.assertEquals(spot_ids[inner_top.pk], 2, "Inner top was selected")
        self.assertEquals(spot_ids[inner_bottom.pk], 2, "Inner bottom was selected")

        # Testing limits - should get all of the inner and mid, but no outer spots
        response = c.get("/api/v1/spot", { 'center_latititude':center_lat, 'center_longitude':center_long, 'distance':101 ,'limit':8})
        self.assertEquals(response.status_code, 200, "Accepts the distance query")
        spots = json.loads(response.content)
        self.assertEquals(len(spots), 8, "Returns 8 spots")
        spot_ids = {
            inner_left.pk : 1,
            inner_right.pk : 1,
            inner_top.pk : 1,
            inner_bottom.pk : 1,
            mid_left.pk : 1,
            mid_right.pk : 1,
            mid_top.pk : 1,
            mid_bottom.pk : 1,
        }
        for spot in spots:
            self.assertEquals(spot_ids[spot.pk], 1, "Spot matches a unique inner or mid spot")
            spot_ids[spot.pk] = 2

        # Testing limits - should get all inner and mid spots, and 2 outer spots
        response = c.get("/api/v1/spot", { 'center_latititude':center_lat, 'center_longitude':center_long, 'distance':101 ,'limit':10})
        self.assertEquals(response.status_code, 200, "Accepts the distance query")
        spots = json.loads(response.content)
        self.assertEquals(len(spots), 10, "Returns 10 spots")
        spot_ids = {
            inner_left.pk : 1,
            inner_right.pk : 1,
            inner_top.pk : 1,
            inner_bottom.pk : 1,
            mid_left.pk : 1,
            mid_right.pk : 1,
            mid_top.pk : 1,
            mid_bottom.pk : 1,
            outer_left.pk : 1,
            outer_right.pk : 1,
            outer_top.pk : 1,
            outer_bottom.pk : 1,
        }
        for spot in spots:
            self.assertEquals(spot_ids[spot.pk], 1, "Spot matches a unique inner, mid or outer spot")
            spot_ids[spot.pk] = 2


        self.assertEquals(spot_ids[inner_left.pk], 2, "Inner left was selected")
        self.assertEquals(spot_ids[inner_right.pk], 2, "Inner right was selected")
        self.assertEquals(spot_ids[inner_top.pk], 2, "Inner top was selected")
        self.assertEquals(spot_ids[inner_bottom.pk], 2, "Inner bottom was selected")

        self.assertEquals(spot_ids[mid_left.pk], 2, "Mid left was selected")
        self.assertEquals(spot_ids[mid_right.pk], 2, "Mid rightwas selected")
        self.assertEquals(spot_ids[mid_top.pk], 2, "Mid top was selected")
        self.assertEquals(spot_ids[mid_bottom.pk], 2, "Mid bottom was selected")

        # Testing that limit 0 = no limit - get all 12 spots
        response = c.get("/api/v1/spot", { 'center_latititude':center_lat, 'center_longitude':center_long, 'distance':110, 'limit': 0 })
        self.assertEquals(response.status_code, 200, "Accepts the distance query")
        spots = json.loads(response.content)
        self.assertEquals(len(spots), 12, "Returns 12 spots with a limit of 0")
        spot_ids = {
            inner_left.pk : 1,
            inner_right.pk : 1,
            inner_top.pk : 1,
            inner_bottom.pk : 1,
            mid_left.pk : 1,
            mid_right.pk : 1,
            mid_top.pk : 1,
            mid_bottom.pk : 1,
            outer_left.pk : 1,
            outer_right.pk : 1,
            outer_top.pk : 1,
            outer_bottom.pk : 1,
        }
        for spot in spots:
            self.assertEquals(spot_ids[spot.pk], 1, "Spot matches a unique inner, mid or outer spot")
            spot_ids[spot.pk] = 2


        # Testing that the default limit is 20 spaces
        response = c.get("/api/v1/spot", { 'center_latititude':center_lat, 'center_longitude':center_long, 'distance':130 })
        self.assertEquals(response.status_code, 200, "Accepts the distance query")
        spots = json.loads(response.content)
        self.assertEquals(len(spots), 20, "Returns 20 spots with no defined limit")
        spot_ids = {
            inner_left.pk : 1,
            inner_right.pk : 1,
            inner_top.pk : 1,
            inner_bottom.pk : 1,
            mid_left.pk : 1,
            mid_right.pk : 1,
            mid_top.pk : 1,
            mid_bottom.pk : 1,
            outer_left.pk : 1,
            outer_right.pk : 1,
            outer_top.pk : 1,
            outer_bottom.pk : 1,
        }

        far_out_count = 0
        for spot in spots:
            if spot.pk in spot_ids:
                self.assertEquals(spot_ids[spot.pk], 1, "Spot matches a unique inner, mid or outer spot")
            else:
                far_out_count += 1

        self.assertEquals(far_out_count, 8, "Found 8 far out spots to fill in the limit of 20")

        # Testing that with a limit of 0, we pull in all spots in range
        response = c.get("/api/v1/spot", { 'center_latititude':center_lat, 'center_longitude':center_long, 'distance':130, 'limit':0 })
        self.assertEquals(response.status_code, 200, "Accepts the distance query")
        spots = json.loads(response.content)
        self.assertEquals(len(spots), 112, "Returns 112 spots with a limit of 0")
        spot_ids = {
            inner_left.pk : 1,
            inner_right.pk : 1,
            inner_top.pk : 1,
            inner_bottom.pk : 1,
            mid_left.pk : 1,
            mid_right.pk : 1,
            mid_top.pk : 1,
            mid_bottom.pk : 1,
            outer_left.pk : 1,
            outer_right.pk : 1,
            outer_top.pk : 1,
            outer_bottom.pk : 1,
        }

        far_out_count = 0
        for spot in spots:
            if spot.pk in spot_ids:
                self.assertEquals(spot_ids[spot.pk], 1, "Spot matches a unique inner, mid or outer spot")
            else:
                far_out_count += 1

        self.assertEquals(far_out_count, 100, "Found all 100 far out spots")





