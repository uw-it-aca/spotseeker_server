from spotseeker_server.views.rest_dispatch import RESTDispatch
from spotseeker_server.forms.spot import SpotForm
from spotseeker_server.models import Spot
from django.http import HttpResponse
from spotseeker_server.require_auth import *
import simplejson as json

class SpotView(RESTDispatch):
    @app_auth_required
    def GET(self, request, spot_id):
        try:
            spot = Spot.objects.get(pk=spot_id)
            return HttpResponse("This is the RESTy view for spot id: "+spot_id)
        except:
            response = HttpResponse("Spot not found")
            response.status_code = 404
            return response


    @user_auth_required
    def PUT(self, request, spot_id):
        body = request.read()
        new_values = json.loads(body)
        form = SpotForm(new_values)

        if form.is_valid():
            return HttpResponse("Passes validation")
        else:
            response = HttpResponse(json.dumps(form.errors))
            response.status_code = 400
            return response

    @user_auth_required
    def DELETE(self, request, spot_id):
        return HttpResponse("This should be a DELETE for spot id: "+spot_id)
