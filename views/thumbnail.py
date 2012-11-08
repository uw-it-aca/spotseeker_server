from spotseeker_server.views.rest_dispatch import RESTDispatch
from spotseeker_server.models import SpotImage, Spot
from django.http import HttpResponse
from django.utils.http import http_date
from spotseeker_server.require_auth import *
from cStringIO import StringIO
import Image
import time


class ThumbnailView(RESTDispatch):
    """ Returns 200 with a thumbnail of a SpotImage.
    """
    @app_auth_required
    def GET(self, request, spot_id, image_id, thumb_width=None, thumb_height=None, constrain=False):
        if constrain is True:
            # im.thumbnail needs two dimensions, and they can be the same since we're limiting
            if thumb_width is None:
                thumb_width = thumb_height

            if thumb_height is None:
                thumb_height = thumb_width

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

        if constrain is True:
            im.thumbnail((thumb_width, thumb_height, Image.ANTIALIAS))
            thumb = im
        else:
            thumb = im.resize((thumb_width, thumb_height), Image.ANTIALIAS)

        tmp = StringIO()
        thumb.save(tmp, im.format, quality=92)
        tmp.seek(0)

        response = HttpResponse(tmp.getvalue())
        # 7 day timeout?
        response['Expires'] = http_date(time.time() + 60 * 60 * 24 * 7)
        response["Content-type"] = img.content_type
        return response
