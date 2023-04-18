# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" Changes
    =================================================================

    sbutler1@illinois.edu: adapt to the new RESTDispatch framework.
"""
import time

from spotseeker_server.views.rest_dispatch import (
    RESTDispatch,
    RESTException,
    JSONResponse,
)
from django.http import HttpResponse
from django.utils.http import http_date
from wsgiref.util import FileWrapper
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from spotseeker_server.require_auth import *
from spotseeker_server.models import *


class ItemImageView(RESTDispatch):
    """Handles actions at /api/v1/item/<item id>/image/<image id>.
    GET returns 200 with the image.
    PUT returns 200 and updates the image.
    DELETE returns 200 and deletes the image.
    """

    @app_auth_required
    def GET(self, request, item_id, image_id):
        img = ItemImage.objects.get(pk=image_id)
        item = img.item

        if int(item.pk) != int(item_id):
            raise RESTException(
                "Image Spot ID doesn't match item id in url", 404
            )

        response = HttpResponse(FileWrapper(img.image))
        response["ETag"] = img.etag

        # 7 day timeout?
        response["Expires"] = http_date(time.time() + 60 * 60 * 24 * 7)
        response["Content-length"] = img.image.size
        response["Content-type"] = img.content_type
        return response

    # @admin_auth_required
    def PUT(self, request, item_id, image_id):
        img = ItemImage.objects.get(pk=image_id)
        item = img.item

        if int(item.pk) != int(item_id):
            raise RESTException(
                "Image Spot ID doesn't match spot id in url", 404
            )

        self.validate_etag(request, img)

        request.method = "POST"
        request._load_post_and_files()
        request.method = "PUT"

        if "image" in request.META["files"]:
            img.image = ImageFile(request.META["files"]["image"])
        if "description" in request.META["files"]:
            img.description = request.META["files"]["description"]
        if "display_index" in request.META["files"]:
            img.display_index = request.META["files"]["display_index"]
        img.save()
        item.spot.save()

        return self.GET(request, item_id, image_id)

    # @admin_auth_required
    def DELETE(self, request, item_id, image_id):
        img = ItemImage.objects.get(pk=image_id)
        item = img.item

        if int(item.pk) != int(item_id):
            raise RESTException(
                "Image Item ID doesn't match item id in url", 404
            )

        img.delete()
        item.spot.save()

        return HttpResponse(status=200)
