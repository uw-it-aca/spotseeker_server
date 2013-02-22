from spotseeker_server.views.rest_dispatch import RESTDispatch
from spotseeker_server.forms.spot import SpotForm
from spotseeker_server.models import *
from django.http import HttpResponse
from spotseeker_server.require_auth import *
import simplejson as json
from django.core.cache import cache

class AllSpotsView(RESTDispatch):
    
    @app_auth_required
    def GET(self, request):
        spots = Spot.objects.all()
        response = []
        for spot in spots:
            if (cache.get(spot.pk)):
                spot_json = cache.get(spot.pk)
            else:
                spot_json = spot.json_data_structure()
                cache.add(spot.pk, spot_json)
            response.append(spot_json)
        return HttpResponse(response)
