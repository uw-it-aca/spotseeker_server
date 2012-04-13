from spotseeker_server.views.rest_dispatch import RESTDispatch
from spotseeker_server.models import SpotImage, Spot#, UploadTestImage
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from spotseeker_server.require_auth import *
from PIL import Image

class AddImageView(RESTDispatch):
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
            image = spot.spotimage_set.create( image=request.FILES["image"] )
        except ValidationError:
            response = HttpResponse('"error":"Not an accepted image format"}')
            response.status_code = 400
            return response

        if "description" in request.POST:
            image.description = request.POST["description"]

        image.save()

        response = HttpResponse()
        response.status_code = 201
        response["Location"] = image.rest_url()

        return response


