# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

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


class NoRESTMethodsTest(TestCase):
    def test_no_GET(self):
        c = Client()
        response = c.get("/api/v1/null")
        self.assertEquals(response.status_code, 405)

    def test_no_POST(self):
        c = Client()
        response = c.post("/api/v1/null")
        self.assertEquals(response.status_code, 405)

    def test_no_DELETE(self):
        c = Client()
        response = c.delete("/api/v1/null")
        self.assertEquals(response.status_code, 405)

    def test_no_PUT(self):
        c = Client()
        response = c.put("/api/v1/null")
        self.assertEquals(response.status_code, 405)

    def test_no_HEAD(self):
        c = Client()
        response = c.head("/api/v1/null")
        self.assertEquals(response.status_code, 405)

    def test_no_OPTIONS(self):
        c = Client()
        response = c.options("/api/v1/null")
        self.assertEquals(response.status_code, 405)
