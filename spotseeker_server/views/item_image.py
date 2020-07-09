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

    Changes
    =================================================================

    sbutler1@illinois.edu: adapt to the new RESTDispatch framework.
"""
import time

from spotseeker_server.views.rest_dispatch import \
    RESTDispatch, RESTException, JSONResponse
from django.http import HttpResponse
from django.utils.http import http_date
from wsgiref.util import FileWrapper
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from spotseeker_server.require_auth import *
from spotseeker_server.models import *


class ItemImageView(RESTDispatch):
    """ Handles actions at /api/v1/item/<item id>/image/<image id>.
    GET returns 200 with the image.
    PUT returns 200 and updates the image.
    DELETE returns 200 and deletes the image.
    """
    @app_auth_required
    def get(self, request, item_id, image_id, *args, **kwargs):
        img = ItemImage.objects.get(pk=image_id)
        item = img.item

        if int(item.pk) != int(item_id):
            raise RESTException("Image Spot ID doesn't match item id in url",
                                404)

        response = HttpResponse(FileWrapper(img.image))
        response["ETag"] = img.etag

        # 7 day timeout?
        response['Expires'] = http_date(time.time() + 60 * 60 * 24 * 7)
        response["Content-length"] = img.image.size
        response["Content-type"] = img.content_type
        return response

    @user_auth_required
    @admin_auth_required
    def put(self, request, item_id, image_id, *args, **kwargs):
        img = ItemImage.objects.get(pk=image_id)
        item = img.item

        if int(item.pk) != int(item_id):
            raise RESTException("Image Spot ID doesn't match spot id in url",
                                404)

        self.validate_etag(request, img)

        request.method = "POST"
        request._load_post_and_files()
        request.method = "PUT"

        if "image" in request.META['files']:
            img.image = ImageFile(request.META['files']["image"])
        if "description" in request.META['files']:
            img.description = request.META['files']["description"]
        if "display_index" in request.META['files']:
            img.display_index = request.META['files']["display_index"]
        img.save()
        item.spot.save()

        return self.get(request, item_id, image_id)

    @user_auth_required
    @admin_auth_required
    def delete(self, request, item_id, image_id, *args, **kwargs):
        img = ItemImage.objects.get(pk=image_id)
        item = img.item

        if int(item.pk) != int(item_id):
            raise RESTException("Image Item ID doesn't match item id in url",
                                404)

        img.delete()
        item.spot.save()

        return HttpResponse(status=200)
