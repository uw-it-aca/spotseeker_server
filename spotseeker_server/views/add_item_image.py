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

    sbutler1@illinois.edu: adapt to a simplier RESTDispatch framework.
"""

from spotseeker_server.views.rest_dispatch import RESTDispatch, RESTException
from spotseeker_server.models import ItemImage, Item
from django.http import HttpResponse
from spotseeker_server.require_auth import *
from PIL import Image


class AddItemImageView(RESTDispatch):
    """ Saves a ItemImage for a particular Item on POST to
        /api/v1/item/<item id>/image.
    """
    @user_auth_required
    @admin_auth_required
    def POST(self, request, item_id):
        item = Item.objects.get(pk=item_id)

        if "image" not in request.FILES:
            raise RESTException("No image", 400)

        args = {
            'upload_application': request.META.get('SS_OAUTH_CONSUMER_NAME',
                                                   ''),
            'upload_user': request.META.get('SS_OAUTH_USER', ''),
            'description': request.POST.get('description', ''),
            'display_index': request.POST.get('display_index'),
            'image': request.FILES['image']
        }
        if args['display_index'] is None:
            # TODO: is there a better way?
            # get display_indexes for all of the existing images
            # and set the new one to the biggest + 1
            indices = [img.display_index for img in item.itemimage_set.all()]
            if indices:
                args['display_index'] = max(indices) + 1
            else:
                args['display_index'] = 0

        image = item.itemimage_set.create(**args)
        item.spot.save()

        response = HttpResponse(status=201)
        response["Location"] = image.rest_url()

        return response
