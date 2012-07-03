from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot, SpotAvailableHours
import simplejson as json


class SpotHoursPUTTest(TestCase):

    def test_hours(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                       SPOTSEEKER_SPOT_FORM='spotseeker_server.default_forms.spot.DefaultSpotForm'):
            spot = Spot.objects.create(name="This spot has available hours")
            etag = spot.etag

            put_obj = {
                'name': "This spot has available hours",
                'capacity': "4",
                'location': {
                     'latitude': '55',
                     'longitude': '30',
                },
                'available_hours': {
                    'monday': [["00:00", "10:00"], ["11:00", "14:00"]],
                    'tuesday': [["11:00", "14:00"]],
                    'wednesday': [["11:00", "14:00"]],
                    'thursday': [["11:00", "14:00"]],
                    'friday': [["11:00", "14:00"]],
                    'saturday': [],
                    'sunday': [["11:00", "14:00"]],
                }
            }

            c = Client()
            url = "/api/v1/spot/%s" % spot.pk
            response = c.put(url, json.dumps(put_obj), content_type="application/json", If_Match=etag)
            spot_dict = json.loads(response.content)

            self.maxDiff = None
            self.assertEquals(spot_dict["available_hours"], put_obj["available_hours"], "Data from the web service matches the data for the spot")
