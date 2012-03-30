from django.utils import unittest
from django.test.client import Client
from spotseeker_server.models import Spot
import simplejson as json

class SpotSearchFieldTest(unittest.TestCase):
    def test_fields(self):
        spot1 = Spot.objects.create(name = "This is a searchable Name - OUGL")
        spot1.save()

        spot2 = Spot.objects.create(name = "This OUGL is an alternative spot")
        spot2.save()

        spot3 = Spot.objects.create(name = "3rd spot")
        spot3.save()

        spot4 = Spot.objects.create(name = "OUGL  - 3rd spot in the site")
        spot4.save()

        c = Client()
        response = c.get("/api/v1/spot", { 'name':'OUGL' })
        self.assertEquals(response.status_code, 200, "Accepts name query")
        spots = json.loads(response.content)
        self.assertEquals(len(spots), 3, 'Find 3 matches for OUGL')

        spot_ids = {
            spot1.pk: 1,
            spot2.pk: 1,
            spot4.pk: 1,
        }

        for spot in spots:
            self.assertEquals(spot_ids[spot.id], 1, "Includes each spot, uniquely")
            spot_ids[spot.id] = 2

        # This part is essentially imagination...
        spot5 = Spot.objects.create(name = "Has whiteboards", has_whiteboards = True)
        spot5.save()
        spot6 = Spot.objects.create(name = "Has no whiteboards", has_whiteboards = False)
        spot6.save()

        response = c.get("/api/v1/spot", { 'has_whiteboards':True })
        self.assertEquals(response.status_code, 200, "Accepts whiteboards query")
        spots = json.loads(response.content)
        self.assertEquals(len(spots), 1, 'Finds 1 match for whiteboards')

        self.assertEquals(spots[0].id, spot5.pk, "Finds spot5 w/ a whiteboard")

        spot7 = Spot.objects.create(name = "Text search for the title - Odegaard Undergraduate Library and Learning Commons", has_whiteboards = True)
        spot7.save()

        response = c.get("/api/v1/spot", { 'has_whiteboards':True, 'name':'odegaard under' })
        self.assertEquals(response.status_code, 200, "Accepts whiteboards + name query")
        spots = json.loads(response.content)
        self.assertEquals(len(spots), 1, 'Finds 1 match for whiteboards + odegaard')

        self.assertEquals(spots[0].id, spot7.pk, "Finds spot7 w/ a whiteboard + odegaard")



