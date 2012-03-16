from spotseeker_server.views.rest_dispatch import RESTDispatch
from django.http import HttpResponse
from spotseeker_server.require_auth import *

class AddImageView(RESTDispatch):
    @user_auth_required
    def POST(self, request, spot_id):
        return HttpResponse("Add an image to spot: "+spot_id)


