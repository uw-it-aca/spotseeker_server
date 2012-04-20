from spotseeker_server.views.rest_dispatch import RESTDispatch
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from spotseeker_server.require_auth import *
from spotseeker_server.models import *

class ImageView(RESTDispatch):
    @app_auth_required
    def GET(self, request, spot_id, image_id):
        try:
            img = SpotImage.objects.get(pk=image_id)
            spot = img.spot

            if int(spot.pk) != int(spot_id):
                raise Exception("Image Spot ID doesn't match spot id in url")

            response = HttpResponse(FileWrapper(img.image))
            response["ETag"] = img.etag
            response["Content-length"] = img.image.size
            response["Content-type"] = img.content_type
            return response
        except Exception as e:
            print "E: ", e
            response = HttpResponse('{"error":"Bad Image URL"}')
            response.status_code = 404
            return response

    @user_auth_required
    def PUT(self, request, spot_id, image_id):
        try:
            img = SpotImage.objects.get(pk=image_id)
            spot = img.spot

            if int(spot.pk) != int(spot_id):
                raise Exception("Image Spot ID doesn't match spot id in url")

            error_response = self.validate_etag(request, img)
            if error_response:
                return error_response

        except Exception as e:
            response = HttpResponse('{"error":"Bad Image URL"}')
            response.status_code = 404
            return response


        # This trick was taken from piston
        request.method = "POST"
        request._load_post_and_files()
        request.method = "PUT"

        if "image" in request.FILES:
            try:
                img.image = request.FILES["image"]
                img.save()
            except ValidationError:
                response = HttpResponse('"error":"Not an accepted image format"}')
                response.status_code = 400
                return response

        if "description" in request.POST:
            img.description = request.POST["description"]

        return self.GET(request, spot_id, image_id)


    @user_auth_required
    def DELETE(self, request, spot_id, image_id):
        try:
            img = SpotImage.objects.get(pk=image_id)
            spot = img.spot

            if int(spot.pk) != int(spot_id):
                raise Exception("Image Spot ID doesn't match spot id in url")

            error_response = self.validate_etag(request, img)
            if error_response:
                return error_response

        except Exception as e:
            response = HttpResponse('{"error":"Bad Image URL"}')
            response.status_code = 404
            return response

        img.delete()

        response = HttpResponse("")
        response.status_code = 200

        return response

    # Utility methods...
    def validate_etag(self, request, img):
        if not "If_Match" in request.META:
            response = HttpResponse('{"error":"If-Match header required"}')
            response.status_code = 409
            return response

        if request.META["If_Match"] != img.etag:
            response = HttpResponse('{"error":"Invalid ETag"}')
            response.status_code = 409
            return response



