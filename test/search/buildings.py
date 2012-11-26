from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot, SpotExtendedInfo
import simplejson as json


class BuildingSearchTest(TestCase):
    """ Tests the /api/v1/buildings interface.
    """
    def test_buildings_for_campus(self):
        spot1 = Spot.objects.create(name="Spot on campus A.", building_name="Aay building")
        spot2 = Spot.objects.create(name="Spot on campus B.", building_name="Bee building")

        campusa = SpotExtendedInfo.objects.create(spot=spot1, key="campus", value="seattle")
        campusa.save()
        campusb = SpotExtendedInfo.objects.create(spot=spot2, key="campus", value="tacoma")
        campusb.save()

        c = Client()

        response = c.get("/api/v1/buildings")
        buildings = json.loads(response.content)
        self.assertEquals(len(buildings), 2, 'Full Building list returns 2 building.')

        response = c.get("/api/v1/buildings", {"campus": "seattle"})
        buildings = json.loads(response.content)

        self.assertEquals(len(buildings), 1, 'Seattle building list only returns 1 building.')
        # Assert that the building returned is not from the tacoma campus.
        # Assert that the building returned is from the seattle campus.

        response = c.get("/api/v1/buildings", {"campus": "tacoma"})
        buildings = json.loads(response.content)

        self.assertEquals(len(buildings), 1, 'Seattle building list only returns 1 building.')
        # Assert that the building returned is not from the seattle campus.
        # Assert that the building returned is from the tacoma campus.
