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

from __future__ import print_function
from spotseeker_server.views.rest_dispatch import RESTDispatch, RESTException, RESTFormInvalidError
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
        spot = Spot.get_with_external(spot_id)
        response = HttpResponse(json.dumps(spot.json_data_structure()))
        response["ETag"] = spot.etag
        response["Content-type"] = "application/json"
        return response

    @user_auth_required
    def POST(self, request):
        return self.build_and_save_from_input(request, None)

    @user_auth_required
    def PUT(self, request, spot_id):
        spot = Spot.get_with_external(spot_id)

        self.validate_etag(request, spot)

        return self.build_and_save_from_input(request, spot)

    @user_auth_required
    def DELETE(self, request, spot_id):
        spot = Spot.get_with_external(spot_id)

        self.validate_etag(request, spot)

        spot.delete()
        response = HttpResponse()
        response.status_code = 200
        return response

    # These are utility methods for the HTTP methods
    @transaction.commit_on_success
    def build_and_save_from_input(self, request, spot):
        body = request.read()
        try:
            json_values = json.loads(body)
        except Exception as e:
            raise RESTException("Unable to parse JSON", status_code=400)

        # Fix up the spot types array into IDs
        types = json_values.pop('type', None)
        if types is not None:
            if isinstance(types, basestring):
                types = (types,)

            json_values['spottypes'] = []
            for typename in types:
                t = SpotType.objects.get(name=typename)
                json_values['spottypes'].append(t.pk)

        # Unnest the location object
        if 'location' in json_values:
            for loc_key in json_values['location']:
                json_values[loc_key] = json_values['location'][loc_key]
            del json_values['location']

        # Save the extended_info for later
        new_extended_info = json_values.pop('extended_info', None)
        old_extended_info = {}
        if spot is not None:
            old_extended_info = dict((ei.key, ei.value) for ei in spot.spotextendedinfo_set.all())

        # Save the available hours for later
        available_hours = json_values.pop('available_hours', None)

        # Remve excluded fields
        excludefields = set(SpotForm.Meta.exclude)
        for fieldname in excludefields:
            if fieldname in json_values:
                del json_values[fieldname]

        if spot is None:
            form = SpotForm(json_values)
            is_new = True
        else:
            # Copy over the existing values
            for field in spot._meta.fields:
                if field.name in excludefields:
                    continue
                if not field.name in json_values:
                    json_values[field.name] = getattr(spot, field.name)

            # spottypes is not included in the above copy, do it manually
            if not 'spottypes' in json_values:
                json_values['spottypes'] = [t.pk for t in spot.spottypes.all()]

            form = SpotForm(json_values, instance=spot)
            is_new = False

        if not form.is_valid():
            raise RESTFormInvalidError(form)

        spot = form.save()

        # sync extended info
        if new_extended_info is None:
            # TODO: I don't believe this is the correct thing to do
            SpotExtendedInfo.objects.filter(spot=spot).delete()
        else:
            # first, loop over the new extended info and either:
            # - add items that are new
            # - update items that are old
            for key in new_extended_info:
                value = new_extended_info[key]

                if not key in old_extended_info:
                    eiform = SpotExtendedInfoForm({'spot':spot.pk, 'key':key, 'value':value})
                elif value == old_extended_info[key]:
                    continue
                else:
                    ei = SpotExtendedInfo.objects.get(spot=spot, key=key)
                    eiform = SpotExtendedInfoForm({'spot':spot.pk, 'key':key, 'value':value}, instance=ei)

                if not eiform.is_valid():
                    raise RESTFormInvalidError(eiform)
            
                ei = eiform.save()
            # Now loop over the different in the keys and remove old
            # items that aren't present in the new set
            for key in (set(old_extended_info.keys()) - set(new_extended_info.keys())):
                try:
                    ei = SpotExtendedInfo.objects.get(spot=spot, key=key)
                    ei.delete()
                except SpotExtendedInfo.DoesNotExist:
                    # removing something that does not exist isn't an error
                    pass

        # sync available hours
        if available_hours is not None:
            SpotAvailableHours.objects.filter(spot=spot).delete()

            for day in SpotAvailableHours.DAY_CHOICES:
                if not day[1] in available_hours:
                    continue

                day_hours = available_hours[day[1]]
                for window in day_hours:
                    SpotAvailableHours.objects.create(spot=spot, day=day[0], start_time=window[0], end_time=window[1])

        if is_new:
            response = HttpResponse()
            response.status_code = 201
            response['Location'] = spot.rest_url()
        else:
            response = HttpResponse(json.dumps(spot.json_data_structure()))
            response.status_code = 200
        response["ETag"] = spot.etag
        response["Content-type"] = 'application/json'
        return response
