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

from spotseeker_server.views.rest_dispatch import RESTDispatch
from spotseeker_server.models import SpotImage, Spot
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from spotseeker_server.require_auth import *
from PIL import Image


class AddImageView(RESTDispatch):
    """ Saves a SpotImage for a particular Spot on POST to /api/v1/spot/<spot id>/image.
    """
    @user_auth_required
    def POST(self, request, spot_id):
        try:
            spot = Spot.objects.get(pk=spot_id)
        except:
            response = HttpResponse('{"error":"Spot not found"}')
            response.status_code = 404
            return response

        if not "image" in request.FILES:
            response = HttpResponse('"error":"No image"}')
            response.status_code = 400
            return response

        try:
            upload_user = ''
            upload_app = ''
            if 'SS_OAUTH_CONSUMER_NAME' in request.META:
                upload_app = request.META['SS_OAUTH_CONSUMER_NAME']
            if 'SS_OAUTH_USER' in request.META:
                upload_user = request.META['SS_OAUTH_USER']
            image = spot.spotimage_set.create(image=request.FILES["image"], upload_user=upload_user, upload_application=upload_app)
        except ValidationError:
            response = HttpResponse('"error":"Not an accepted image format"}')
            response.status_code = 400
            return response
        except Exception as e:
            response = HttpResponse('"error":"Not an accepted image format"}')
            response.status_code = 400
            return response

        if "description" in request.POST:
            image.description = request.POST["description"]

        response = HttpResponse()
        response.status_code = 201
        response["Location"] = image.rest_url()

        return response
