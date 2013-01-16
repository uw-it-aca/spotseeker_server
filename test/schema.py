from spotseeker_server.models import *
from django.test.client import Client
from django.test import TestCase
import simplejson as json

class SpotSchemaTest(TestCase):
    def test_spot_types(self):
        SpotType.objects.create(name="Jedi")
        SpotType.objects.create(name="Sith")

        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        schema_types = schema["type"]

        self.assertEquals(len(schema_types), 2, "The Schema SpotType match the actual SpotType")
        SpotType.objects.create(name="Ewok")

        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        schema_types = schema["type"]

        self.assertEquals(len(schema_types), 3, "The Schema SpotType match the actual SpotType")

    def test_extended_info(self):
        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        extended_info = schema["extended_info"]

        self.assertEquals(2, 2, "This is just a place holder test for the extended_info schema. There is no real test here yet, except 2 does equal 2.")
