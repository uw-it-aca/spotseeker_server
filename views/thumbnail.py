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

from spotseeker_server.views.rest_dispatch import RESTDispatch, RESTException
from spotseeker_server.models import SpotImage, Spot
from django.http import HttpResponse
from django.utils.http import http_date
from spotseeker_server.require_auth import *
from cStringIO import StringIO
import Image
import time


class ThumbnailView(RESTDispatch):
    """ Returns 200 with a thumbnail of a SpotImage.
    """
    @app_auth_required
    def GET(self, request, spot_id, image_id, thumb_width=None, thumb_height=None, constrain=False):
        img = SpotImage.objects.get(pk=image_id)
        spot = img.spot

        if int(spot.pk) != int(spot_id):
            raise Exception("Image Spot ID doesn't match spot id in url")

        if constrain is True:
            if thumb_width is None:
                thumb_width = img.width

            if thumb_height is None:
                thumb_height = img.height

        thumb_width = int(thumb_width)
        thumb_height = int(thumb_height)

        if thumb_height <= 0 or thumb_width <= 0:
            raise RESTException("Bad image constraints", 400)

        image = img.image
        im = Image.open(image.path)

        if constrain is True:
            im.thumbnail((thumb_width, thumb_height, Image.ANTIALIAS))
            thumb = im
        else:
            thumb = im.resize((thumb_width, thumb_height), Image.ANTIALIAS)

        tmp = StringIO()
        thumb.save(tmp, im.format, quality=95)
        tmp.seek(0)

        response = HttpResponse(tmp.getvalue())
        # 7 day timeout?
        response['Expires'] = http_date(time.time() + 60 * 60 * 24 * 7)
        response["Content-type"] = img.content_type
        return response
