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
from spotseeker_server.models import SpotImage, Spot
from django.http import HttpResponse
from spotseeker_server.require_auth import *
from PIL import Image


class AddImageView(RESTDispatch):
    """ Saves a SpotImage for a particular Spot on POST to /api/v1/spot/<spot id>/image.
    """
    @user_auth_required
    @admin_auth_required
    def POST(self, request, spot_id):
        spot = Spot.objects.get(pk=spot_id)

        if not "image" in request.FILES:
            raise RESTException("No image", 400)

        args = {}
        args['upload_application'] = request.META.get('SS_OAUTH_CONSUMER_NAME', '')
        args['upload_user'] = request.META.get('SS_OAUTH_USER', '')
        args['description'] = request.POST.get('description', '')

        args['display_index'] = request.POST.get('display_index')
        if args['display_index'] is None:
            #TODO: is there a better way?
            # get display_indexes for all of the existing images and set the new one to the biggest + 1
            indexes = []
            for img in spot.spotimage_set.all():
                indexes.append(img.display_index)
            indexes.sort()
            try:
                args['display_index'] = indexes[-1] + 1
            except IndexError:
                args['display_index'] = 0

        args['image'] = request.FILES['image']

        image = spot.spotimage_set.create(**args)

        response = HttpResponse(status=201)
        response["Location"] = image.rest_url()

        return response
