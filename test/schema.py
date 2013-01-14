from spotseeker_server.models import *
from django.test.client import Client
from django.test import TestCase
import simplejson as json

class SpotSchemaTest(TestCase):
    def test_spot_types(self):
        SpotType.objects.create(name="Jedi")
        SpotType.objects.create(name="Sith")
        SpotType.objects.create(name="Ewok")

        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        schema_types = schema["type"]

        self.assertEquals(len(schema_types), 3, "The Schema SpotType match the actual SpotType")
