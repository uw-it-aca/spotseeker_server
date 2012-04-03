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
            response = HttpResponse(json.dumps(spot.json_data_structure()))
            response["ETag"] = spot.etag
            response["Content-type"] = "application/json"
            return response
        except:
            response = HttpResponse("Spot not found")
            response.status_code = 404
            return response


    @user_auth_required
    def PUT(self, request, spot_id):
        body = request.read()
        try:
            new_values = json.loads(body)
        except Exception as e:
            response = HttpResponse('{"error":"Unable to parse JSON"}')
            response.status_code = 400
            return response

        try:
            spot = Spot.objects.get(pk=spot_id)
        except Exception as e:
            response = HttpResponse('{"error":"Spot not found"}')
            response.status_code = 404
            return response

        form = SpotForm(new_values)


        if not "If_Match" in request.META:
            response = HttpResponse('{"error":"If-Match header required"}')
            response.status_code = 409
            return response

        if request.META["If_Match"] != spot.etag:
            response = HttpResponse('{"error":"Invalid ETag"}')
            response.status_code = 409
            return response

        if not form.is_valid():
            response = HttpResponse(json.dumps(form.errors))
            response.status_code = 400
            return response

        spot.name = new_values["name"]
        spot.capacity = new_values["capacity"]
        spot.save()


        return self.GET(request, spot_id)
#        return HttpResponse("Passes validation")

    @user_auth_required
    def DELETE(self, request, spot_id):
        try:
            spot = Spot.objects.get(pk=spot_id)
        except Exception as e:
            response = HttpResponse('{"error":"Spot not found"}')
            response.status_code = 404
            return response

        if not "If_Match" in request.META:
            response = HttpResponse('{"error":"If-Match header required"}')
            response.status_code = 409
            return response

        if request.META["If_Match"] != spot.etag:
            response = HttpResponse('{"error":"Invalid ETag"}')
            response.status_code = 409
            return response


        spot.delete()
        response = HttpResponse()
        response.status_code = 410
        return response
