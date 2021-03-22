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
import shutil
import tempfile
try:
    from cStringIO import StringIO as IOStream
except ModuleNotFoundError:
    from io import BytesIO as IOStream

from spotseeker_server.test.images import ImageTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import Client
from spotseeker_server.models import Spot, SpotImage
from PIL import Image
from os.path import abspath, dirname
from django.test.utils import override_settings


TEST_ROOT = abspath(dirname(__file__))
image_folder = '%s/../resources' % TEST_ROOT


@override_settings(SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
                   SPOTSEEKER_AUTH_ADMINS=('demo_user',))
class ImageThumbTest(ImageTestCase):

    def setUp(self):
        self.TEMP_DIR = tempfile.mkdtemp()
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            spot = Spot.objects.create(
                name="This is to test thumbnailing images"
            )
            self.spot = spot
            self.url = '/api/v1/spot/%s/image' % spot.pk

    def tearDown(self):
        shutil.rmtree(self.TEMP_DIR)

    def assertContentType(self, response, expected_type):

        self.assertEquals(
            response['Content-type'],
            expected_type,
            'Got wrong content type for response'
        )

    def test_all_thumbs(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = self.client

            image_formats = (
                ('image/jpeg', 'JPEG', '%s/test_jpeg.jpg' % image_folder),
                ('image/png', 'PNG', '%s/test_png.png' % image_folder),
                ('image/gif', 'GIF', '%s/test_gif.gif' % image_folder),
            )
            # Width/height pairs of dimensions which should return an
            # image with the original width/height
            good_dimensions = (
                (100, 100),
                (1, 100),
                (100, 1),
                (1, 1),
                (200, 200)
            )

            # Bad pairs which should result in 400s
            # Width, Height, Comment
            bad_dimensions = (
                (100, 0, 'missing height'),
                (0, 100, 'missing width'),
                (0, 0, 'missing both'),
                (100, -100, 'negative height'),
                (-100, 100, 'negative width'),
                ('a', 100, 'invalid width'),
                (100, 'a', 'invalid height')
            )

            for content_type, img_format, image_name in image_formats:

                response = self.upload_image(
                    image_name, self.url,
                    {'description': 'this is a %s' % img_format})
                new_base_location = response["Location"]

                for width, height in good_dimensions:
                    img_url = '%s/thumb/%sx%s' % (
                        new_base_location, width, height
                    )
                    response = c.get(img_url)

                    self.assertEqual(
                        response.status_code,
                        200,
                        'Expected 200 for %sx%s (%s)'
                        % (width, height, img_format))
                    self.assertContentType(response, content_type)
                    data = IOStream(response.content)
                    im = Image.open(data)
                    self.assertEquals(
                        im.format, img_format,
                        'img format did not match'
                    )
                    self.assertEquals(
                        im.size[0], width,
                        'img width did not match (%s)' % img_format
                    )
                    self.assertEquals(
                        im.size[1], height,
                        'img height did not match (%s)' % img_format
                    )

                for width, height, comment in bad_dimensions:

                    img_url = '%s/thumb/%sx%s' % (
                        new_base_location, width, height
                    )
                    response = c.get(img_url)
                    self.assertEquals(
                        response.status_code, 400,
                        'Expected 400 for image with width %s and'
                        ' height %s (%s)' % (width, height, comment)
                    )

    def test_invalid_url(self):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = Client()
            bad_spot = Spot.objects.create(name="This is the wrong spot")

            spot = Spot.objects.create(name="This is to test getting images")
            gif = SpotImage.objects.create(
                description='This is the GIF test',
                spot=spot,
                image=SimpleUploadedFile(
                    "test_gif.gif",
                    open(
                        "%s/../resources/test_gif.gif" % TEST_ROOT, 'rb'
                    ).read(),
                    'image/gif'
                )
            )

            url = '/api/v1/spot/%s/image/%s/thumb/10x10' % (
                bad_spot.pk, gif.pk
            )
            response = c.get(url)
            self.assertEquals(
                response.status_code,
                404,
                "Give a 404 for a spot id that doesn't match the image's"
            )

    def assertImageRatio(self, im, ratio):

        im_ratio = float(im.size[0]) / float(im.size[1])
        self.assertAlmostEqual(im_ratio, ratio, places=1)

    def test_constrain_jpeg(self):
        self._test_aspect_ratio('image/jpeg',
                                'JPEG',
                                '%s/test_jpeg2.jpg' % image_folder)

    def test_constrain_png(self):
        self._test_aspect_ratio('image/png',
                                'PNG',
                                '%s/test_png2.png' % image_folder)

    def test_constrain_gif(self):
        self._test_aspect_ratio('image/gif',
                                'GIF',
                                '%s/test_gif2.gif' % image_folder)

    def _test_aspect_ratio(self, content_type, img_format, img_file):
        with self.settings(MEDIA_ROOT=self.TEMP_DIR):
            c = self.client
            response = self.upload_image(
                img_file,
                self.url,
                {'description': 'test %s #2' % img_format})

            orig_im = Image.open(img_file)
            orig_ratio = float(orig_im.size[0]) / float(orig_im.size[1])

            new_base_location = response['Location']

            def get_thumb_constrained(**kwargs):
                args = ','.join('%s:%s' % x for x in kwargs.items())
                url = '%s/thumb/constrain/%s' % (new_base_location, args)
                response = c.get(url)
                return response

            # 50 width test
            response = get_thumb_constrained(width=50)
            self.assertContentType(response, content_type)
            im = Image.open(IOStream(response.content))
            self.assertEquals(im.size[0], 50, '%s Should have been 50 width')
            self.assertImageRatio(im, orig_ratio)
            self.assertEquals(
                im.format, img_format, '%s Format was not the same'
            )

            # 50 height test
            response = get_thumb_constrained(height=50)
            self.assertContentType(response, content_type)
            im = Image.open(IOStream(response.content))
            self.assertEquals(im.size[1], 50, 'Should have been 50 height')
            self.assertImageRatio(im, orig_ratio)
            self.assertEquals(im.format, img_format, 'Format was not the same')

            # 75 width, 50 height
            # Should result in 50 height
            response = get_thumb_constrained(width=75, height=50)
            self.assertContentType(response, content_type)
            im = Image.open(IOStream(response.content))
            self.assertEquals(im.size[1], 50, 'Should have been 50 height')
            self.assertImageRatio(im, orig_ratio)
            self.assertEquals(im.format, img_format, 'Format was not the same')

            # 50 width, 75 height
            # Should result in 50 height
            response = get_thumb_constrained(width=50, height=75)
            self.assertContentType(response, content_type)
            im = Image.open(IOStream(response.content))
            self.assertEquals(im.size[1], 75, 'Should have been 75 height')
            self.assertImageRatio(im, orig_ratio)
            self.assertEquals(im.format, img_format, 'Format was not the same')
