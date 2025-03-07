# Copyright 2024 UW-IT, University of Washington
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
from spotseeker_server.models import *
from oauth2_provider.views.generic import ReadWriteScopedResourceView


class ImageView(RESTDispatch, ReadWriteScopedResourceView):
    """Handles actions at /api/v1/spot/<spot id>/image/<image id>.
    GET returns 200 with the image.
    PUT returns 200 and updates the image.
    DELETE returns 200 and deletes the image.
    """

    def get(self, request, spot_id, image_id):
        img = SpotImage.objects.get(pk=image_id)
        spot = img.spot

        if int(spot.pk) != int(spot_id):
            raise RESTException(
                "Image Spot ID doesn't match spot id in url", 404
            )

        response = HttpResponse(FileWrapper(img.image))
        response["ETag"] = img.etag

        # 7 day timeout?
        response["Expires"] = http_date(time.time() + 60 * 60 * 24 * 7)
        response["Content-length"] = img.image.size
        response["Content-type"] = img.content_type
        return response

    def put(self, request, spot_id, image_id):
        img = SpotImage.objects.get(pk=image_id)
        spot = img.spot

        if int(spot.pk) != int(spot_id):
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

        return self.get(request, spot_id, image_id)

    def delete(self, request, spot_id, image_id):
        img = SpotImage.objects.get(pk=image_id)
        spot = img.spot

        if int(spot.pk) != int(spot_id):
            raise RESTException(
                "Image Spot ID doesn't match spot id in url", 404
            )

        self.validate_etag(request, img)

        img.delete()

        return HttpResponse(status=200)
