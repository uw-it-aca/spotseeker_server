from spotseeker_server.views.rest_dispatch import RESTDispatch
from spotseeker_server.require_auth import *
from spotseeker_server.models import Spot
from django.http import HttpResponse
from django.core.exceptions import FieldError
import simplejson as json


class BuildingListView(RESTDispatch):
    """ Performs actions on the list of buildings, at /api/v1/buildings.
    GET returns 200 with a list of buildings.
    """
    @app_auth_required
    def GET(self, request):
        spots = Spot.objects.all()
        for key, value in request.GET.items():
            try:
                spots = Spot.objects.filter(**{key: value})
            except FieldError:
                # If a FieldError is thrown, the key is probably SpotExtendedInfo
                spots = Spot.objects.filter(spotextendedinfo__key=key, spotextendedinfo__value=value)

        q = spots.values('building_name').distinct()

        buildings = []
        for building in list(q):
            buildings.append(building["building_name"])

        buildings.sort()
        return HttpResponse(json.dumps(buildings))
