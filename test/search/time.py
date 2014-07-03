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
from spotseeker_server.models import Spot, SpotAvailableHours

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

        availhours = SpotAvailableHours.objects.create(spot=spot, day="th", start_time="11:00:00", end_time="23:59:59")
        availhours2 = SpotAvailableHours.objects.create(spot=spot, day="f", start_time="00:00:00", end_time="16:00:00")
        availhours3 = SpotAvailableHours.objects.create(spot=spot2, day="f", start_time="11:00:00", end_time="16:00:00")

        c = Client()

        response = c.get('/api/v1/spot/', { 'open_at': "Thursday,11:00", 'open_until': "Friday,14:00"}, content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This spot is to test time ranges in search")
        self.assertContains(response, "This is a second spot to test time ranges in search")

        response = c.get('/api/v1/spot/', { 'open_at': "Tuesday,11:00", 'open_until': "Wednesday,15:00"}, content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "[]")

    def SameDayTimeInReverse(self):
        pass

    def FullWeek(self):
        pass

    def tearDown(self):
        pass
