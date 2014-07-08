""" Copyright 2012, 2013 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from spotseeker_server.models import Spot, SpotAvailableHours


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok')
class SpotSearchTimeTest(TestCase):

    def setUp(self):
        pass

    def SameDayTimeInSerial(self):

        spot = Spot.objects.create(name="This spot is to test time ranges in search")
        spot.save()

        spot2 = Spot.objects.create(name="This is a second spot to test time ranges in search")
        spot2.save()

        availhours = SpotAvailableHours.objects.create(spot=spot, day="f", start_time="11:00:00", end_time="16:00:00")
        availhours2 = SpotAvailableHours.objects.create(spot=spot2, day="f", start_time="11:00:00", end_time="16:00:00")

        c = Client()

        response = c.get('/api/v1/spot/', { 'open_at': "Friday,11:00", 'open_until': "Friday,14:00"}, content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This spot is to test time ranges in search")

        response = c.get('/api/v1/spot/', { 'open_at': "Thursday,11:00", 'open_until': "Thursday,15:00"}, content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "[]")

    def DiffDayTimeInSerial(self):

        spot = Spot.objects.create(name="This spot is to test time ranges in search")
        spot.save()

        spot2 = Spot.objects.create(name="This is a second spot to test time ranges in search")
        spot2.save()

        spot3 = Spot.objects.create(name="This is a third spot to test time ranges in search")
        spot3.save()

        availhoursmon = SpotAvailableHours.objects.create(spot=spot, day="m", start_time="00:00:00", end_time="13:00:00")
        availhoursmon2 = SpotAvailableHours.objects.create(spot=spot, day="m", start_time="14:00:00", end_time="23:59:59")
        availhourstues = SpotAvailableHours.objects.create(spot=spot, day="t", start_time="00:00:00", end_time="23:59:59")
        availhoursweds = SpotAvailableHours.objects.create(spot=spot, day="w", start_time="00:00:00", end_time="23:59:59")
        availhoursthurs = SpotAvailableHours.objects.create(spot=spot, day="th", start_time="00:00:00", end_time="23:59:59")
        availhoursfri = SpotAvailableHours.objects.create(spot=spot, day="f", start_time="00:00:00", end_time="23:59:59")
        availhourssat = SpotAvailableHours.objects.create(spot=spot, day="sa", start_time="00:00:00", end_time="23:59:59")
        availhourssun = SpotAvailableHours.objects.create(spot=spot, day="su", start_time="00:00:00", end_time="23:59:59")

        availhoursmon3 = SpotAvailableHours.objects.create(spot=spot2, day="m", start_time="00:00:00", end_time="13:00:00")
        availhourstues2 = SpotAvailableHours.objects.create(spot=spot2, day="t", start_time="00:00:00", end_time="23:59:59")
        availhoursweds2 = SpotAvailableHours.objects.create(spot=spot2, day="w", start_time="00:00:00", end_time="23:59:59")
        availhoursthurs2 = SpotAvailableHours.objects.create(spot=spot2, day="th", start_time="00:00:00", end_time="23:59:59")
        availhoursfri2 = SpotAvailableHours.objects.create(spot=spot2, day="f", start_time="00:00:00", end_time="08:00:00")
        availhoursfri3 = SpotAvailableHours.objects.create(spot=spot2, day="f", start_time="09:00:00", end_time="23:59:59")
        availhourssat2 = SpotAvailableHours.objects.create(spot=spot2, day="sa", start_time="00:00:00", end_time="23:59:59")
        availhourssun2 = SpotAvailableHours.objects.create(spot=spot2, day="su", start_time="00:00:00", end_time="23:59:59")


        availhoursmon4 = SpotAvailableHours.objects.create(spot=spot3, day="m", start_time="00:00:00", end_time="23:59:59")
        availhourstues3 = SpotAvailableHours.objects.create(spot=spot3, day="t", start_time="00:00:00", end_time="23:59:59")
        availhoursweds3 = SpotAvailableHours.objects.create(spot=spot3, day="w", start_time="00:00:00", end_time="23:59:59")
        availhoursthurs3 = SpotAvailableHours.objects.create(spot=spot3, day="th", start_time="00:00:00", end_time="13:00:00")
        availhoursthurs4 = SpotAvailableHours.objects.create(spot=spot3, day="th", start_time="14:00:00", end_time="23:59:59")
        availhoursfri4 = SpotAvailableHours.objects.create(spot=spot3, day="f", start_time="00:00:00", end_time="23:59:59")
        availhourssat3 = SpotAvailableHours.objects.create(spot=spot3, day="sa", start_time="00:00:00", end_time="23:59:59")
        availhourssun3 = SpotAvailableHours.objects.create(spot=spot3, day="su", start_time="00:00:00", end_time="23:59:59")


        c = Client()

        response = c.get('/api/v1/spot/', { 'open_at': "Monday,10:00", 'open_until': "Friday,10:00"}, content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, "This spot is to test time ranges in search")
        self.assertNotContains(response, "This is a second spot to test time ranges in search")
        self.assertNotContains(response, "This is a third spot to test time ranges in search")

    def SameDayTimeInReverse(self):
        spot = Spot.objects.create(name="This spot is to test time ranges in search")
        spot.save()

        spot2 = Spot.objects.create(name="This is a second spot to test time ranges in search")
        spot2.save()

        spot3 = Spot.objects.create(name="Third spot, same purpose")
        spot3.save()

        spot4 = Spot.objects.create(name="Fourth spot, same purpose")
        spot4.save()

        availhoursmon = SpotAvailableHours.objects.create(spot=spot, day="m", start_time="00:00:00", end_time="23:59:59")
        availhourstues = SpotAvailableHours.objects.create(spot=spot, day="t", start_time="00:00:00", end_time="23:59:59")
        availhoursweds = SpotAvailableHours.objects.create(spot=spot, day="w", start_time="00:00:00", end_time="23:59:59")
        availhoursthurs = SpotAvailableHours.objects.create(spot=spot, day="th", start_time="00:00:00", end_time="23:59:59")
        availhoursfri = SpotAvailableHours.objects.create(spot=spot, day="f", start_time="00:00:00", end_time="23:59:59")
        availhourssat = SpotAvailableHours.objects.create(spot=spot, day="sa", start_time="00:00:00", end_time="23:59:59")
        availhourssun = SpotAvailableHours.objects.create(spot=spot, day="su", start_time="00:00:00", end_time="23:59:59")

        availhours2 = SpotAvailableHours.objects.create(spot=spot2, day="m", start_time="11:00:00", end_time="14:00:00")

        availhours3 = SpotAvailableHours.objects.create(spot=spot3, day="w", start_time="08:00:00", end_time="17:00:00")

        availhoursmon2 = SpotAvailableHours.objects.create(spot=spot4, day="m", start_time="00:00:00", end_time="11:00:00")
        availhoursmon3 = SpotAvailableHours.objects.create(spot=spot4, day="m", start_time="14:00:00", end_time="23:59:59")
        availhourstues2 = SpotAvailableHours.objects.create(spot=spot4, day="t", start_time="00:00:00", end_time="23:59:59")
        availhoursweds2 = SpotAvailableHours.objects.create(spot=spot4, day="w", start_time="00:00:00", end_time="23:59:59")
        availhoursthurs2 = SpotAvailableHours.objects.create(spot=spot4, day="th", start_time="00:00:00", end_time="23:59:59")
        availhoursfri2 = SpotAvailableHours.objects.create(spot=spot4, day="f", start_time="00:00:00", end_time="23:59:59")
        availhourssat2 = SpotAvailableHours.objects.create(spot=spot4, day="sa", start_time="00:00:00", end_time="23:59:59")
        availhourssun2 = SpotAvailableHours.objects.create(spot=spot4, day="su", start_time="00:00:00", end_time="23:59:59")


        c = Client()

        response = c.get('/api/v1/spot/', { 'open_at': "Monday,15:00", 'open_until': "Monday,10:00"}, content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'This spot is to test time ranges in search')
        self.assertNotContains(response, 'This is a second spot to test time ranges in search')
        self.assertNotContains(response, 'Third spot, same purpose')
        self.assertContains(response, 'Fourth spot, same purpose')

    def FullWeek(self):
        spot = Spot.objects.create(name="This spot is to test time ranges in search")
        spot.save()

        spot2 = Spot.objects.create(name="This is a second spot to test time ranges in search")
        spot2.save()


        availhoursmon = SpotAvailableHours.objects.create(spot=spot, day="m", start_time="00:00:00", end_time="23:59:59")
        availhourstues = SpotAvailableHours.objects.create(spot=spot, day="t", start_time="00:00:00", end_time="23:59:59")
        availhoursweds = SpotAvailableHours.objects.create(spot=spot, day="w", start_time="00:00:00", end_time="23:59:59")
        availhoursthurs = SpotAvailableHours.objects.create(spot=spot, day="th", start_time="00:00:00", end_time="23:59:59")
        availhoursfri = SpotAvailableHours.objects.create(spot=spot, day="f", start_time="00:00:00", end_time="23:59:59")
        availhourssat = SpotAvailableHours.objects.create(spot=spot, day="sa", start_time="00:00:00", end_time="23:59:59")
        availhourssun = SpotAvailableHours.objects.create(spot=spot, day="su", start_time="00:00:00", end_time="23:59:59")

        availhours2 = SpotAvailableHours.objects.create(spot=spot2, day="f", start_time="08:00:00", end_time="17:00:00")

        c = Client()

        response = c.get('/api/v1/spot/', { 'open_at': "Thursday,11:00", 'open_until': "Wednesday,20:00"}, content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This spot is to test time ranges in search")
        self.assertNotContains(response, "This is a second spot to test time ranges in search")



    def tearDown(self):
        pass
