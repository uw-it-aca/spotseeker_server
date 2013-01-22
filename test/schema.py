from spotseeker_server.models import *
from django.test.client import Client
from django.test import TestCase
import simplejson as json


class SpotSchemaTest(TestCase):
    def test_regular_spot_info(self):
        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)

        self.assertEquals(schema["manager"], "unicode", "Schema Regular Spot Info matches the actual Regular Spot Info")
        self.assertEquals(schema["capacity"], "int", "Schema Regular Spot Info matches the actual Regular Spot Info")
        self.assertEquals(schema["last_modified"], "datetime", "Schema Regular Spot Info matches the actual Regular Spot Info")
        self.assertEquals(schema["uri"], "uri", "Schema Regular Spot Info matches the actual Regular Spot Info")

    def test_location_spot_info(self):
        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        schema_location = schema["location"]

        self.assertEquals(schema_location["latitude"], "decimal", "Schema Location Spot Info matches the actual Location Spot Info")
        self.assertEquals(schema_location["room_number"], "unicode", "Schema Location Spot Info matches the actual Location Spot Info")
        self.assertEquals(schema_location["floor"], "unicode", "Schema Location Spot Info matches the actual Location Spot Info")

    def test_spot_image_info(self):
        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        schema_images = schema["images"]

        self.assertEquals(schema_images[0]["description"], "unicode", "Schema Spot Image Info matches the actual Spot Image Info")
        self.assertEquals(schema_images[0]["modification_date"], "datetime", "Schema Spot Image Info matches the actual Spot Image Info")
        self.assertEquals(schema_images[0]["width"], "int", "Schema Spot Image Info matches the actual Spot Image Info")

    def test_spot_types(self):
        SpotType.objects.create(name="Jedi")
        SpotType.objects.create(name="Sith")

        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        schema_types = schema["type"]

        self.assertEquals(len(schema_types), 2, "Schema SpotType matches the actual SpotType")
        SpotType.objects.create(name="Ewok")

        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        schema_types = schema["type"]

        self.assertEquals(len(schema_types), 3, "Schema SpotType matches the actual SpotType")

    def test_extended_info(self):
        test_spot = Spot.objects.create(id=1, name="Test")

        SpotExtendedInfo.objects.create(spot=test_spot, key="noise_level", value=["silent", "quiet", "moderate", "loud", "variable"])
        SpotExtendedInfo.objects.create(spot=test_spot, key="has_computers", value=["true"])
        SpotExtendedInfo.objects.create(spot=test_spot, key="orientation", value="unicode")
        SpotExtendedInfo.objects.create(spot=test_spot, key="num_computers", value="int")

        c = Client()
        response = c.get("/api/v1/schema")
        schema = json.loads(response.content)
        extended_info = schema["extended_info"]

        self.assertEquals(extended_info["noise_level"], ["silent", "quiet", "moderate", "loud", "variable"], "Schema ExtendedInfo matches the actual ExtendedInfo")
        self.assertEquals(extended_info["has_computers"], ["true"], "Schema ExtendedInfo matches the actual ExtendedInfo")
        self.assertEquals(extended_info["orientation"], "unicode", "Schema ExtendedInfo matches the actual ExtendedInfo")
        self.assertEquals(extended_info["num_computers"], "int", "Schema ExtendedInfo matches the actual ExtendedInfo")
