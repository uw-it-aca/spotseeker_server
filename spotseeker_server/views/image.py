from spotseeker_server.views.rest_dispatch import RESTDispatch
from django.http import HttpResponse
from spotseeker_server.require_auth import *

class ImageView(RESTDispatch):
    @app_auth_required
    def GET(self, request, spot_id, image_id):
        return HttpResponse("This should be image data.  spot id: "+spot_id+" image id: "+image_id)

