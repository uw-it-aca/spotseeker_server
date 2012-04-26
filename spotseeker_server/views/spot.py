from spotseeker_server.views.rest_dispatch import RESTDispatch
from spotseeker_server.forms.spot import SpotForm
from spotseeker_server.models import Spot, SpotAvailableHours
from django.http import HttpResponse
from spotseeker_server.require_auth import *
import simplejson as json
from django.db import transaction


class SpotView(RESTDispatch):
    """ Performs actions on a Spot at /api/v1/spot/<spot id>.
    GET returns 200 with Spot details.
    POST to /api/v1/spot with valid JSON returns 200 and creates a new Spot.
    PUT returns 200 and updates the Spot information.
    DELETE returns 200 and deletes the Spot.
    """
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
    def POST(self, request):
        spot = Spot.objects.create()

        error_response = self.build_and_save_from_input(request, spot)
        if error_response:
            return error_response

        response = HttpResponse()
        response.status_code = 201
        response["Location"] = spot.rest_url()
        return response

    @user_auth_required
    def PUT(self, request, spot_id):
        try:
            spot = Spot.objects.get(pk=spot_id)
        except Exception as e:
            response = HttpResponse('{"error":"Spot not found"}')
            response.status_code = 404
            return response

        error_response = self.validate_etag(request, spot)
        if error_response:
            return error_response

        error_response = self.build_and_save_from_input(request, spot)
        if error_response:
            return error_response

        return self.GET(request, spot_id)

    @user_auth_required
    def DELETE(self, request, spot_id):
        try:
            spot = Spot.objects.get(pk=spot_id)
        except Exception as e:
            response = HttpResponse('{"error":"Spot not found"}')
            response.status_code = 404
            return response

        error_response = self.validate_etag(request, spot)
        if error_response:
            return error_response

        spot.delete()
        response = HttpResponse()
        response.status_code = 200
        return response

    # These are utility methods for the HTTP methods
    def validate_etag(self, request, spot):
        if not "If_Match" in request.META:
            response = HttpResponse('{"error":"If-Match header required"}')
            response.status_code = 409
            return response

        if request.META["If_Match"] != spot.etag:
            response = HttpResponse('{"error":"Invalid ETag"}')
            response.status_code = 409
            return response

    @transaction.commit_on_success
    def build_and_save_from_input(self, request, spot):
        body = request.read()
        try:
            new_values = json.loads(body)
        except Exception as e:
            response = HttpResponse('{"error":"Unable to parse JSON"}')
            response.status_code = 400
            return response

        form = SpotForm(new_values)
        if not form.is_valid():
            response = HttpResponse(json.dumps(form.errors))
            response.status_code = 400
            return response

        spot.name = new_values["name"]
        spot.capacity = new_values["capacity"]
        spot.save()

        queryset = SpotAvailableHours.objects.filter(spot=spot)
        queryset.delete()

        if "available_hours" in new_values:
            available_hours = new_values["available_hours"]
            for day in [["m", "monday"],
                        ["t", "tuesday"],
                        ["w", "wednesday"],
                        ["th", "thursday"],
                        ["f", "friday"],
                        ["sa", "saturday"],
                        ["su", "sunday"]]:
                if day[1] in available_hours:
                    day_hours = available_hours[day[1]]
                    for window in day_hours:
                        SpotAvailableHours.objects.create(spot=spot, day=day[0], start_time=window[0], end_time=window[1])
