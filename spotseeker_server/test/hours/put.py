from django.utils import unittest
from django.test.client import Client
from spotseeker_server.models import Spot, SpotAvailableHours
import simplejson as json

class SpotHoursPUTTest(unittest.TestCase):

    def test_hours(self):
        spot = Spot.objects.create( name = "This spot has available hours" )
        etag = spot.etag


        put_obj = {
            'name': "This spot has available hours",
            'capacity': "4",
            'available_hours': {
                'monday': [ [ "00:00", "10:00" ], [ "11:00", "14:00" ] ],
                'tuesday': [ [ "11:00", "14:00" ] ],
                'wednesday': [ [ "11:00", "14:00" ] ],
                'thursday': [ [ "11:00", "14:00" ] ],
                'friday': [ [ "11:00", "14:00" ] ],
                'saturday': [ ],
                'sunday': [ [ "11:00", "14:00" ] ],
            }
        }


        c = Client()
        url = "/api/v1/spot/%s" % spot.pk
        response = c.put(url, json.dumps(put_obj) , content_type="application/json", If_Match=etag )
        spot_dict = json.loads(response.content)

        self.maxDiff = None
        self.assertEquals(spot_dict["available_hours"], put_obj["available_hours"], "Data from the web service matches the data for the spot")




