# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

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
