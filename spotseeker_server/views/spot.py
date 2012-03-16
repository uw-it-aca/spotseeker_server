from spotseeker_server.views.rest_dispatch import RESTDispatch
from django.http import HttpResponse
from spotseeker_server.require_auth import *

class SpotView(RESTDispatch):
    @app_auth_required
    def GET(self, request, spot_id):
        return HttpResponse("This is the RESTy view for spot id: "+spot_id)

    @user_auth_required
    def PUT(self, request, spot_id):
        return HttpResponse("This should be a PUT for spot id: "+spot_id)

    @user_auth_required
    def DELETE(self, request, spot_id):
        return HttpResponse("This should be a DELETE for spot id: "+spot_id)
