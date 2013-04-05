""" Copyright 2012, 2013 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from spotseeker_server.views.rest_dispatch import RESTDispatch
from spotseeker_server.forms.spot import SpotForm
from spotseeker_server.forms.spot_extended_info import SpotExtendedInfoForm
from spotseeker_server.models import *
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
            spot = Spot.get_with_external(spot_id)
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
            spot = Spot.get_with_external(spot_id)
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
            spot = Spot.get_with_external(spot_id)
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
        if not "HTTP_IF_MATCH" in request.META:
            if not "If_Match" in request.META:
                response = HttpResponse('{"error":"If-Match header required"}')
                response.status_code = 409
                return response
            else:
                request.META["HTTP_IF_MATCH"] = request.META["If_Match"]

        if request.META["HTTP_IF_MATCH"] != spot.etag:
            response = HttpResponse('{"error":"Invalid ETag"}')
            response.status_code = 409
            return response

    @transaction.commit_on_success
    def build_and_save_from_input(self, request, spot):
        body = request.read()
        try:
            json_values = json.loads(body)
        except Exception as e:
            response = HttpResponse('{"error":"Unable to parse JSON"}')
            response.status_code = 400
            return response

        # Save the spot types for later
        new_types = set(json_values.pop('type', []))
        old_types = set()
        if spot is not None:
            old_types = set(t.name for t in spot.spottypes)

        # Unnest the location object
        if 'location' in json_values:
            for loc_key in json_values['location']:
                json_values[loc_key] = json_values['location'][loc_key]
            del json_values['location']

        # Save the extended_info for later
        new_extended_info = json_values.pop('extended_info', {})
        old_extended_info = {}
        if spot is not None:
            old_extended_info = dict([(e.key: e.value) for e in spot.spotextendedinfo_set])

        # Save the available hours for later
        available_hours = json_values.pop('available_hours', [])

        # Remve excluded fields
        excludefields = set(SpotForm.Meta.exclude)
        for fieldname in excludeset:
            if fieldname in json_values:
                del json_values[fieldname]

        if spot is None:
            form = SpotForm(json_values)
        else:
            # Copy over the existing values
            for field in spot._meta.fields:
                if fieldname in excludefields:
                    continue
                if not field.name in json_values:
                    json_values[field.name] = getattr(spot, field.name)

            form = SpotForm(json_values, instance=spot)

        if not form.is_valid():
            response = HttpResponse(json.dumps(form.errors))
            response.status_code = 400
            return response

        spot = form.save()

        # sync spot types
        for typename in (new_types - old_types):
            try:
                t = SpotType.objects.get(name=typename)
                spot.spottypes.add(typename)
            except SpotType.DoesNotExist:
                response = HttpResponse(json.dumps({'error': "Spot type '{0}' does not exist".format(typename)}))
                response.status_code = 400
                return response
        for typename in (old_types - new_types):
            try:
                t = SpotType.objects.get(name=typename)
                spot.spottypes.remove(t)
            except SpotType.DoesNotExist:
                # removing something that doesn't exist isn't an error
                pass

        # sync extended info
        for key in new_extended_info:
            value = new_extended_info[value]

            if not key in old_extended_info:
                eiform = SpotExtendedInfoForm({'spot':spot.pk, 'key':key, 'value':value})
            elif value == old_extended_info[key]:
                continue
            else:
                ei = SpotExtendedInfo.objects.get(spot=spot, key=key)
                eiform = SpotExtendedInfoForm({'spot':spot.pk, 'key':key, 'value':value}, instance=ei)

            if not eiform.is_valid():
                response = HttpResponse(json.dumps(form.errors))
                response.status_code = 400
                return response
            
            ei = eiform.save()
        for key in (old_extended_info.keys() - new_extended_info.keys()):
            try:
                ei = SpotExtendedInfo.objects.get(spot=spot, key=key)
                ei.delete()
            except SpotExtendedInfo.DoesNotExist:
                # removing something that does not exist isn't an error
                pass

        queryset = SpotAvailableHours.objects.filter(spot=spot)
        queryset.delete()

        for day in SpotAvailableHours.day.choices:
            if not day[1] in available_hours:
                continue

            day_hours = available_hours[day[1]]
            for window in day_hours:
                SpotAvailableHours.objects.create(spot=spot, day=day[0], start_time=window[0], end_time=window[1])
