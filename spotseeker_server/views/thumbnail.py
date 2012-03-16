from spotseeker_server.views.rest_dispatch import RESTDispatch
from django.http import HttpResponse
from spotseeker_server.require_auth import *

class ThumbnailView(RESTDispatch):
    @app_auth_required
    def GET(self, request, spot_id, image_id, thumb_width, thumb_height):
        return HttpResponse("This should be thumbnailed image data.  spot id: "+spot_id+" image id: "+image_id+ " width: "+thumb_width+" height: "+thumb_height)


