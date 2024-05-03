# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" Changes
    =================================================================

    sbutler1@illinois.edu: move some of the URL parameter parsing into
        here to simplify the URL patterns; adapt to the new RESTDispatch
        framework.
"""

from io import BytesIO as IOStream
from spotseeker_server.views.rest_dispatch import RESTDispatch, RESTException
from spotseeker_server.models import ItemImage, Item
from django.http import HttpResponse
from django.utils.http import http_date
from PIL import Image
import time
import re
from oauth2_provider.views.generic import ReadWriteScopedResourceView

RE_WIDTH = re.compile(r"width:(\d+)")
RE_HEIGHT = re.compile(r"height:(\d+)")
RE_WIDTHxHEIGHT = re.compile(r"^(\d+)x(\d+)$")


class ItemThumbnailView(RESTDispatch, ReadWriteScopedResourceView):
    """Returns 200 with a thumbnail of a ItemImage."""

    def get(self, request, item_id, image_id,
            thumb_dimensions=None, constrain=False):
        img = ItemImage.objects.get(pk=image_id)
        item = img.item

        if int(item.pk) != int(item_id):
            raise RESTException(
                "Image Item ID doesn't match item id in url", 404
            )

        if thumb_dimensions is None:
            raise RESTException("Image constraints required", 400)

        thumb_width = None
        thumb_height = None
        if constrain:
            m = RE_WIDTH.search(thumb_dimensions)
            if m:
                thumb_width = m.group(1)
            m = RE_HEIGHT.search(thumb_dimensions)
            if m:
                thumb_height = m.group(1)

            if thumb_width is None and thumb_height is None:
                raise RESTException("Image constraints required", 400)
            elif thumb_width is None:
                thumb_width = img.width
            elif thumb_height is None:
                thumb_height = img.height
        else:
            m = RE_WIDTHxHEIGHT.match(thumb_dimensions)
            if not m:
                raise RESTException("Image constraints required", 400)
            else:
                thumb_width = m.group(1)
                thumb_height = m.group(2)

        thumb_width = int(thumb_width)
        thumb_height = int(thumb_height)

        if thumb_height <= 0 or thumb_width <= 0:
            raise RESTException("Bad image constraints", 400)

        image = img.image
        im = Image.open(image.file)

        if constrain:
            im.thumbnail((thumb_width, thumb_height), resample=Image.LANCZOS)
            thumb = im
        else:
            thumb = im.resize(
                (thumb_width, thumb_height), resample=Image.LANCZOS
            )

        tmp = IOStream()
        thumb.save(tmp, im.format, quality=95)
        tmp.seek(0)

        response = HttpResponse(tmp.getvalue(), content_type=img.content_type)
        # 7 day timeout?
        response["Expires"] = http_date(time.time() + 60 * 60 * 24 * 7)
        return response
