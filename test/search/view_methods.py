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
from spotseeker_server.views.search import SearchView


class SpotSearchViewMethodsTest(TestCase):
    def test_2_day_range(self):
        view = SearchView()
        days = view.get_days_in_range("m", "t")
        self.assertEquals(len(days), 2, "2 days in a 2 day range")
        self.assertEquals(days[0], "m", "Monday is the first")
        self.assertEquals(days[1], "t", "Tuesday is the second")

    def test_1_day_range(self):
        view = SearchView()
        days = view.get_days_in_range("m", "m")
        self.assertEquals(len(days), 1, "1 day in a 1 day range")
        self.assertEquals(days[0], "m", "Monday is the first")

    def test_week_range(self):
        view = SearchView()
        days = view.get_days_in_range("su", "sa")
        self.assertEquals(len(days), 7, "7 days in a week range")
        self.assertEquals(days[0], "su", "Sunday is the first")
        self.assertEquals(days[1], "m", "Monday is 2")
        self.assertEquals(days[2], "t", "Tuesday is 3")
        self.assertEquals(days[3], "w", "Wednesday is 4")
        self.assertEquals(days[4], "th", "Thursday is 5")
        self.assertEquals(days[5], "f", "Friday is 6")
        self.assertEquals(days[6], "sa", "Saturday is 7")

    def test_around_the_weekend(self):
        view = SearchView()
        days = view.get_days_in_range("th", "w")
        self.assertEquals(len(days), 7, "7 days in a week range")
        self.assertEquals(days[0], "th", "Thursday is 1")
        self.assertEquals(days[1], "f", "Friday is 2")
        self.assertEquals(days[2], "sa", "Saturday is 3")
        self.assertEquals(days[3], "su", "Sunday is 4")
        self.assertEquals(days[4], "m", "Monday is 5")
        self.assertEquals(days[5], "t", "Tuesday is 6")
        self.assertEquals(days[6], "w", "Wednesday is 7")
