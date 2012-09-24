from spotseeker_server.views.rest_dispatch import RESTDispatch
from spotseeker_server.forms.spot import SpotForm
from spotseeker_server.models import *
from django.http import HttpResponse
from spotseeker_server.require_auth import *
import simplejson as json

class AllSpotsView(RESTDispatch):
    
    @app_auth_required
    def GET(self, request):
        spots = Spot.objects.all()
        response = []
        for spot in spots:
            response.append(spot.json_data_structure())
        return HttpResponse(json.dumps(response))
