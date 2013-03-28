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
from spotseeker_server.forms.spot_search import SpotSearchForm
from spotseeker_server.views.spot import SpotView
from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Q
from spotseeker_server.require_auth import *
from spotseeker_server.models import Spot, SpotType
from pyproj import Geod
from decimal import *
import simplejson as json
import re
from time import *
from datetime import datetime
import sys

# UIUC LDAP
from org_filters.uiuc_ldap_client import get_res_street_address

class SearchView(RESTDispatch):
    """ Handles searching for Spots with particular attributes based on a query string.
    """
    @user_auth_required
    def POST(self, request):
        return SpotView().run(request)

    @app_auth_required
    def GET(self, request):
        form = SpotSearchForm(request.GET)
        has_valid_search_param = False

        if not form.is_valid():
            return HttpResponse('[]')

        if len(request.GET) == 0:
            return HttpResponse('[]')

        query = Spot.objects.all()

        day_dict = {"Sunday": "su",
                    "Monday": "m",
                    "Tuesday": "t",
                    "Wednesday": "w",
                    "Thursday": "th",
                    "Friday": "f",
                    "Saturday": "sa", }
        # Exclude things that get special consideration here, otherwise add a filter for the keys
        for key in request.GET:
            if re.search('^oauth_', key):
                pass
            elif key == "expand_radius":
                pass
            elif key == "distance":
                pass
            elif key == "center_latitude":
                pass
            elif key == "center_longitude":
                pass
            elif key == "limit":
                pass
            elif key == "open_now":
                if request.GET["open_now"]:

                    day_lookup = ["su", "m", "t", "w", "th", "f", "sa"]
                    day_num = int(strftime("%w", localtime()))
                    today = day_lookup[day_num]
                    now = datetime.time(datetime.now())
                    query = query.filter(spotavailablehours__day__iexact=today, spotavailablehours__start_time__lt=now, spotavailablehours__end_time__gt=now)
                    has_valid_search_param = True
            elif key == "open_until":
                if request.GET["open_until"] and request.GET["open_at"]:
                    until_day, until_time = request.GET["open_until"].split(',')
                    at_day, at_time = request.GET["open_at"].split(',')
                    until_day = day_dict[until_day]
                    at_day = day_dict[at_day]

                    if until_day == at_day:
                        query = query.filter(spotavailablehours__day__iexact=until_day, spotavailablehours__start_time__lte=at_time, spotavailablehours__end_time__gte=until_time)
                    else:
                        days_to_test = self.get_days_in_range(at_day, until_day)
                        last_day = days_to_test.pop()
                        days_to_test.reverse()
                        first_day = days_to_test.pop()

                        query = query.filter(spotavailablehours__day__iexact=first_day, spotavailablehours__start_time__lte=at_time, spotavailablehours__end_time__gte="23:59")
                        query = query.filter(spotavailablehours__day__iexact=last_day, spotavailablehours__start_time__lte="00:00", spotavailablehours__end_time__gte=until_time)

                        for day in days_to_test:
                            query = query.filter(spotavailablehours__day__iexact=day, spotavailablehours__start_time__lte="00:00", spotavailablehours__end_time__gte="23:59")
                    has_valid_search_param = True
            elif key == "open_at":
                if request.GET["open_at"]:
                    try:
                        request.GET["open_until"]
                    except:
                        day, time = request.GET['open_at'].split(',')
                        day = day_dict[day]
                        query = query.filter(spotavailablehours__day__iexact=day, spotavailablehours__start_time__lte=time, spotavailablehours__end_time__gt=time)
                        has_valid_search_param = True
            elif key == "extended_info:reservable":
                query = query.filter(spotextendedinfo__key="reservable", spotextendedinfo__value__in=['true', 'reservations'])
            elif key == "extended_info:noise_level":
                noise_levels = request.GET.getlist("extended_info:noise_level")

                exclude_silent = True
                exclude_quiet = True
                exclude_moderate = True
                exclude_loud = True
                exclude_variable = True

                for level in noise_levels:
                    if "silent" == level:
                        exclude_silent = False
                    if "quiet" == level:
                        exclude_quiet = False
                        exclude_variable = False
                    if "moderate" == level:
                        exclude_moderate = False
                        exclude_variable = False

                if exclude_silent:
                    query = query.exclude(spotextendedinfo__key="noise_level", spotextendedinfo__value__iexact="silent")
                if exclude_quiet:
                    query = query.exclude(spotextendedinfo__key="noise_level", spotextendedinfo__value__iexact="quiet")
                if exclude_moderate:
                    query = query.exclude(spotextendedinfo__key="noise_level", spotextendedinfo__value__iexact="moderate")
                if exclude_loud:
                    query = query.exclude(spotextendedinfo__key="noise_level", spotextendedinfo__value__iexact="loud")
                if exclude_variable:
                    query = query.exclude(spotextendedinfo__key="noise_level", spotextendedinfo__value__iexact="variable")

            elif key == "capacity":
                try:
                    limit = int(request.GET["capacity"])
                    with_limit = Q(capacity__gte=limit)
                    with_limit |= Q(capacity__isnull=True)
                    query = query.filter(with_limit)
                    has_valid_search_param = True
                except ValueError:
                    # This we don't care about - if someone passes "", or "twenty", just ignore it
                    pass
                except Exception as e:
                    # Do something to complain??
                    pass
            elif key == "type":
                type_values = request.GET.getlist(key)
                q_obj = Q()
                type_qs = [Q(spottypes__name__exact=v) for v in type_values]
                for type_q in type_qs:
                    q_obj |= type_q
                query = query.filter(q_obj).distinct()
                has_valid_search_param = True
            elif key == "building_name":
                building_names = request.GET.getlist(key)
                q_obj = Q()
                type_qs = [Q(building_name__exact=v) for v in building_names]
                for type_q in type_qs:
                    q_obj |= type_q
                query = query.filter(q_obj).distinct()
                has_valid_search_param = True
            elif re.search('^extended_info:', key):
                kwargs = {
                    'spotextendedinfo__key': key[14:],
                    'spotextendedinfo__value__in': request.GET.getlist(key)
                }
                query = query.filter(**kwargs)
                has_valid_search_param = True
            elif key == "id":
                query = query.filter(id__in=request.GET.getlist(key))
                has_valid_search_param = True
            else:
                try:
                    kwargs = {
                        '%s__icontains' % key: request.GET[key]
                    }
                    query = query.filter(**kwargs)
                    has_valid_search_param = True
                except Exception as e:
                    if not request.META['SERVER_NAME'] == 'testserver':
                        print >> sys.stderr, "E: ", e

        limit = 20
        if 'limit' in request.GET:
            if request.GET['limit'] == '0':
                limit = 0
            else:
                limit = int(request.GET['limit'])

        if 'distance' in request.GET and 'center_longitude' in request.GET and 'center_latitude' in request.GET:
            try:
                g = Geod(ellps='clrk66')
                top = g.fwd(request.GET['center_longitude'], request.GET['center_latitude'], 0, request.GET['distance'])
                right = g.fwd(request.GET['center_longitude'], request.GET['center_latitude'], 90, request.GET['distance'])
                bottom = g.fwd(request.GET['center_longitude'], request.GET['center_latitude'], 180, request.GET['distance'])
                left = g.fwd(request.GET['center_longitude'], request.GET['center_latitude'], 270, request.GET['distance'])

                top_limit = "%.8f" % top[1]
                bottom_limit = "%.8f" % bottom[1]
                left_limit = "%.8f" % left[0]
                right_limit = "%.8f" % right[0]

                distance_query = query.filter(longitude__gte=left_limit)

                distance_query = distance_query.filter(longitude__lte=right_limit)
                distance_query = distance_query.filter(latitude__gte=bottom_limit)
                distance_query = distance_query.filter(latitude__lte=top_limit)
                has_valid_search_param = True

                if len(distance_query) > 0 or 'expand_radius' not in request.GET:
                    query = distance_query
                else:
                    # If we're querying everything, let's make sure we only return a limited number of spaces...
                    limit = 10
            except Exception as e:
                if not request.META['SERVER_NAME'] == 'testserver':
                    print >> sys.stderr, "E: ", e
                #query = Spot.objects.all()
        elif 'distance' in request.GET or 'center_longitude' in request.GET or 'center_latitude' in request.GET:
            if 'distance' not in request.GET or 'center_longitude' not in request.GET or 'center_latitude' not in request.GET:
                # If distance, lat, or long are specified in the server request; all 3 must be present.
                return HttpResponseBadRequest("Bad Request")

        if not has_valid_search_param:
            return HttpResponse('[]')

        if limit > 0 and limit < len(query):
            sorted_list = list(query)
            try:
                sorted_list.sort(lambda x, y: cmp(self.distance(x, request.GET['center_longitude'], request.GET['center_latitude']), self.distance(y, request.GET['center_longitude'], request.GET['center_latitude'])))
                query = sorted_list[:limit]
            except KeyError:
                response = HttpResponse('{"error":"missing required parameters for this type of search"}')
                response.status_code = 400
                return response

        response = []


# UIUC Residence Limits for Labs
# --------------------------------
# Remove any spots that the current user cannot use (i.e. login, print, etc)
        # TODO: Add to settings...
        # UIUC_REQUIRE_ADDRESS = settings.UIUC_REQUIRE_ADDRESS
        UIUC_REQUIRE_ADDRESS = 'uiuc_require_address'

# TODO: Net_ID needs to come from somehwere...

        # Prefect restrictions
        query = query.select_related('SpotExtendedInfo')

        all_the_spots = set(query)

        email = request.GET.get('email_address')

        full_address = ''
        if email:
            full_address = get_res_street_address(email)
        for spot in all_the_spots: 
            if net_id:
                LOGGER.info("User is logged in. Show only spots they may access.")
                address_restrictions = spot.spotextendedinfo_set.get(
                    key=UIUC_REQUIRE_ADDRESS)
                if len(address_restrictions) == 0:
                    response.append(spot.json_data_structure())
                    LOGGER.debug("Not restricted.")
                else:
                    restrict_rule = address_restrictions[0]
                    regex_text = restrict_rule.value
                    if re.match(full_address, regex_text):
                        response.append(spot.json_data_structure())
                        LOGGER.debug("Restricted, user address matches.")
                    else:
                        LOGGER.debug("Restricted, no address match.")
            else:
                LOGGER.info("User is not logged in. Show all spots.")
                response.append(spot.json_data_structure())

        return HttpResponse(json.dumps(response))

    def distance(self, spot, longitude, latitude):
        g = Geod(ellps='clrk66')
        az12, az21, dist = g.inv(spot.longitude, spot.latitude, longitude, latitude)
        return dist

    def get_days_in_range(self, start_day, until_day):
        day_lookup = ["su", "m", "t", "w", "th", "f", "sa", "su", "m", "t", "w", "th", "f", "sa"]
        matched_days = []
        add_days = False

        for day in day_lookup:
            if day == start_day:
                add_days = True
            if add_days:
                matched_days.append(day)

            if day == until_day and add_days is True:
                return matched_days

        return []
