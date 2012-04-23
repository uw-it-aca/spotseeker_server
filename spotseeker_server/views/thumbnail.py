from spotseeker_server.views.rest_dispatch import RESTDispatch
from spotseeker_server.models import SpotImage, Spot
from django.http import HttpResponse
from spotseeker_server.require_auth import *
from cStringIO import StringIO
import Image


class ThumbnailView(RESTDispatch):
    @app_auth_required
    def GET(self, request, spot_id, image_id, thumb_width, thumb_height):
        try:
            img = SpotImage.objects.get(pk=image_id)
            spot = img.spot

            if int(spot.pk) != int(spot_id):
                raise Exception("Image Spot ID doesn't match spot id in url")

            thumb_width = int(thumb_width)
            thumb_height = int(thumb_height)

        except Exception as e:
            response = HttpResponse('{"error":"Bad Image URL"}')
            response.status_code = 404
            return response

        if thumb_height <= 0 or thumb_width <= 0:
            response = HttpResponse('{"error":"Bad Image URL"}')
            response.status_code = 404
            return response

        image = img.image
        im = Image.open(image.path)

        thumb = im.resize((thumb_width, thumb_height), Image.ANTIALIAS)

        tmp = StringIO()
        thumb.save(tmp, im.format)
        tmp.seek(0)

        response = HttpResponse(tmp.getvalue())
        response["Content-type"] = img.content_type
        return response
