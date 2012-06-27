from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from spotseeker_server.models import Spot, SpotExtendedInfo, SpotType
import simplejson as json


class SpotSearchCapacityTest(TestCase):
    def test_capacity(self):
        with self.settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok'):
            spot1 = Spot.objects.create(name="capacity: 1", capacity=1)
            spot1.save()

            spot2 = Spot.objects.create(name="capacity: 2", capacity=2)
            spot2.save()

            spot3 = Spot.objects.create(name="capacity: 3", capacity=3)
            spot3.save()

            spot4 = Spot.objects.create(name="capacity: 4", capacity=4)
            spot4.save()

            spot5 = Spot.objects.create(name="capacity: 50", capacity=4)
            spot5.save()

            c = Client()
            response = c.get("/api/v1/spot", {'capacity': ''})
            spots = json.loads(response.content)

            has_1 = False
            has_2 = False
            has_3 = False
            has_4 = False
            has_5 = False

            for spot in spots:
                if spot['id'] == spot1.pk:
                    has_1 = True
                if spot['id'] == spot2.pk:
                    has_2 = True
                if spot['id'] == spot3.pk:
                    has_3 = True
                if spot['id'] == spot4.pk:
                    has_4 = True
                if spot['id'] == spot5.pk:
                    has_5 = True

            self.assertEquals(has_1, True)
            self.assertEquals(has_2, True)
            self.assertEquals(has_3, True)
            self.assertEquals(has_4, True)
            self.assertEquals(has_5, True)

            response = c.get("/api/v1/spot", {'capacity': '1'})
            spots = json.loads(response.content)

            has_1 = False
            has_2 = False
            has_3 = False
            has_4 = False
            has_5 = False

            for spot in spots:
                if spot['id'] == spot1.pk:
                    has_1 = True
                if spot['id'] == spot2.pk:
                    has_2 = True
                if spot['id'] == spot3.pk:
                    has_3 = True
                if spot['id'] == spot4.pk:
                    has_4 = True
                if spot['id'] == spot5.pk:
                    has_5 = True

            self.assertEquals(has_1, True)
            self.assertEquals(has_2, True)
            self.assertEquals(has_3, True)
            self.assertEquals(has_4, True)
            self.assertEquals(has_5, True)

            response = c.get("/api/v1/spot", {'capacity': '49'})
            spots = json.loads(response.content)

            has_1 = False
            has_2 = False
            has_3 = False
            has_4 = False
            has_5 = False

            for spot in spots:
                if spot['id'] == spot1.pk:
                    has_1 = True
                if spot['id'] == spot2.pk:
                    has_2 = True
                if spot['id'] == spot3.pk:
                    has_3 = True
                if spot['id'] == spot4.pk:
                    has_4 = True
                if spot['id'] == spot5.pk:
                    has_5 = True

            self.assertEquals(has_1, False)
            self.assertEquals(has_2, False)
            self.assertEquals(has_3, False)
            self.assertEquals(has_4, False)
            self.assertEquals(has_5, True)

            response = c.get("/api/v1/spot", {'capacity': '501'})
            spots = json.loads(response.content)

            has_1 = False
            has_2 = False
            has_3 = False
            has_4 = False
            has_5 = False

            for spot in spots:
                if spot['id'] == spot1.pk:
                    has_1 = True
                if spot['id'] == spot2.pk:
                    has_2 = True
                if spot['id'] == spot3.pk:
                    has_3 = True
                if spot['id'] == spot4.pk:
                    has_4 = True
                if spot['id'] == spot5.pk:
                    has_5 = True

            self.assertEquals(has_1, False)
            self.assertEquals(has_2, False)
            self.assertEquals(has_3, False)
            self.assertEquals(has_4, False)
            self.assertEquals(has_5, False)


