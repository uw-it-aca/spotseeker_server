from spotseeker_server.views.rest_dispatch import RESTDispatch
from django.http import HttpResponse
from spotseeker_server.require_auth import *

class SearchView(RESTDispatch):
    @app_auth_required
    def GET(self, request):
        return HttpResponse("This is the RESTy view for spot search")


