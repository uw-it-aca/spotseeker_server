# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from os.path import abspath, dirname
from PIL import Image
from spotseeker_server.models import Spot, SpotImage
import datetime
import simplejson as json

TEST_ROOT = abspath(dirname(__file__))


@override_settings(
    SPOTSEEKER_OAUTH_ENABLED=False,
    SPOTSEEKER_SPOT_FORM="spotseeker_server.default_forms.spot."
    "DefaultSpotForm",
)
class SpotResourceImageTest(TestCase):
    def setUp(self):
        self.TEMP_DIR = tempfile.mkdtemp()
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            spot = Spot.objects.create(
                name="This is to test images in the spot resource"
            )
            self.spot = spot

            gif = SpotImage.objects.create(
                description="This is the GIF test",
                display_index=1,
                spot=spot,
                image=SimpleUploadedFile(
                    "test_gif.gif",
                    open(
                        "%s/../resources/test_gif.gif" % TEST_ROOT, "rb"
                    ).read(),
                    "image/gif",
                ),
            )
            self.gif = gif

            jpeg = SpotImage.objects.create(
                description="This is the JPEG test",
                display_index=0,
                spot=spot,
                image=SimpleUploadedFile(
                    "test_jpeg.jpg",
                    open(
                        "%s/../resources/test_jpeg.jpg" % TEST_ROOT, "rb"
                    ).read(),
                    "image/jpeg",
                ),
            )
            self.jpeg = jpeg

            png = SpotImage.objects.create(
                description="This is the PNG test",
                spot=spot,
                image=SimpleUploadedFile(
                    "test_png.png",
                    open(
                        "%s/../resources/test_png.png" % TEST_ROOT, "rb"
                    ).read(),
                    "image/png",
                ),
            )
            self.png = png

    def tearDown(self):
        shutil.rmtree(self.TEMP_DIR)

    def test_empty_image_data(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            spot = Spot.objects.create(name="A spot with no images")

            c = Client()
            response = c.get("/api/v1/spot/{0}".format(spot.pk))
            spot_dict = json.loads(response.content)

            self.assertEquals(len(spot_dict["images"]), 0)

    def test_image_order(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            response = c.get("/api/v1/spot/{0}".format(self.spot.pk))

            spot_dict = json.loads(response.content)

            images_fr_json = spot_dict["images"]
            images_fr_db = SpotImage.objects.filter(spot=self.spot).order_by(
                "display_index"
            )

            # I'm not entirely happy with this batch of assertions, but
            # right now don't have any better ideas
            self.assertEquals(
                images_fr_json[0]["description"], "This is the PNG test"
            )
            self.assertEquals(
                images_fr_json[1]["description"], "This is the JPEG test"
            )
            self.assertEquals(
                images_fr_json[2]["description"], "This is the GIF test"
            )

    def test_image_data(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            response = c.get("/api/v1/spot/{0}".format(self.spot.pk))

            spot_dict = json.loads(response.content)

            self.assertEquals(len(spot_dict["images"]), 3, "Has 3 images")

            has_gif = False
            has_png = False
            has_jpg = False
            for image in spot_dict["images"]:
                one_sec = datetime.timedelta(seconds=1)
                if image["id"] == self.gif.pk:
                    has_gif = True
                    self.assertEquals(
                        image["url"],
                        "/api/v1/spot/{0}/image/{1}".format(
                            self.spot.pk, self.gif.pk
                        ),
                    )
                    self.assertEquals(
                        image["thumbnail_root"],
                        "/api/v1/spot/{0}/image/{1}/thumb".format(
                            self.spot.pk, self.gif.pk
                        ),
                    )
                    self.assertEquals(image["content-type"], "image/gif")
                    img = Image.open(
                        "%s/../resources/test_gif.gif" % TEST_ROOT
                    )
                    self.assertEquals(image["width"], img.size[0])
                    self.assertEquals(image["height"], img.size[1])

                    # I have no idea if this will fail under TZs other than
                    # UTC, but here we go
                    # Creation and modification dates will NOT be the same,
                    # but should hopefully be w/in one second
                    create = datetime.datetime.strptime(
                        image["creation_date"], "%Y-%m-%dT%H:%M:%S.%f+00:00"
                    )
                    mod = datetime.datetime.strptime(
                        image["modification_date"],
                        "%Y-%m-%dT%H:%M:%S.%f+00:00",
                    )
                    delta = mod - create
                    self.assertTrue(
                        delta < one_sec,
                        "creation_date and modification_date are "
                        + "less than one second apart",
                    )

                    self.assertEquals(image["upload_user"], "")
                    self.assertEquals(image["upload_application"], "")
                    self.assertEquals(image["display_index"], 1)

                if image["id"] == self.png.pk:
                    has_png = True
                    self.assertEquals(
                        image["url"],
                        "/api/v1/spot/{0}/image/{1}".format(
                            self.spot.pk, self.png.pk
                        ),
                    )
                    self.assertEquals(
                        image["thumbnail_root"],
                        "/api/v1/spot/{0}/image/{1}/thumb".format(
                            self.spot.pk, self.png.pk
                        ),
                    )
                    self.assertEquals(image["content-type"], "image/png")
                    img = Image.open(
                        "%s/../resources/test_png.png" % TEST_ROOT
                    )
                    self.assertEquals(image["width"], img.size[0])
                    self.assertEquals(image["height"], img.size[1])

                    # I have no idea if this will fail under TZs other than
                    # UTC, but here we go
                    # Creation and modification dates will NOT be the same,
                    # but should hopefully be w/in one second
                    create = datetime.datetime.strptime(
                        image["creation_date"], "%Y-%m-%dT%H:%M:%S.%f+00:00"
                    )
                    mod = datetime.datetime.strptime(
                        image["modification_date"],
                        "%Y-%m-%dT%H:%M:%S.%f+00:00",
                    )
                    delta = mod - create
                    self.assertTrue(
                        delta < one_sec,
                        "creation_date and modification_date are "
                        "less than one second apart",
                    )

                    self.assertEquals(image["upload_user"], "")
                    self.assertEquals(image["upload_application"], "")

                if image["id"] == self.jpeg.pk:
                    has_jpg = True
                    self.assertEquals(
                        image["url"],
                        "/api/v1/spot/{0}/image/{1}".format(
                            self.spot.pk, self.jpeg.pk
                        ),
                    )
                    self.assertEquals(
                        image["thumbnail_root"],
                        "/api/v1/spot/{0}/image/{1}/thumb".format(
                            self.spot.pk, self.jpeg.pk
                        ),
                    )
                    self.assertEquals(image["content-type"], "image/jpeg")
                    img = Image.open(
                        "%s/../resources/test_jpeg.jpg" % TEST_ROOT
                    )
                    self.assertEquals(image["width"], img.size[0])
                    self.assertEquals(image["height"], img.size[1])

                    # I have no idea if this will fail under TZs other than
                    # UTC, but here we go
                    # Creation and modification dates will NOT be the same,
                    # but should hopefully be w/in one second
                    create = datetime.datetime.strptime(
                        image["creation_date"], "%Y-%m-%dT%H:%M:%S.%f+00:00"
                    )
                    mod = datetime.datetime.strptime(
                        image["modification_date"],
                        "%Y-%m-%dT%H:%M:%S.%f+00:00",
                    )
                    delta = mod - create
                    self.assertTrue(
                        delta < one_sec,
                        "creation_date and modification_date are "
                        "less than one second apart",
                    )

                    self.assertEquals(image["upload_user"], "")
                    self.assertEquals(image["upload_application"], "")
                    self.assertEquals(image["display_index"], 0)

            self.assertEquals(has_gif, True, "Found the gif")
            self.assertEquals(has_jpg, True, "Found the jpg")
            self.assertEquals(has_png, True, "Found the png")
