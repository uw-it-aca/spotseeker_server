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

        return HttpResponse("This should be image data.  spot id: "+spot_id+" image id: "+image_id)

