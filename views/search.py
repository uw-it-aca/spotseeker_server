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

    Changes
    =================================================================

    sbutler1@illinois.edu: adapt to the new RESTDispatch framework;
        remove some needless use of regex; add open_anytime option;
        move some UW options into new org_filter; add org_filter
        support (hooks).
"""

from spotseeker_server.views.rest_dispatch import RESTDispatch, RESTException, JSONResponse
from spotseeker_server.forms.spot_search import SpotSearchForm
from spotseeker_server.views.spot import SpotView
from spotseeker_server.org_filters import SearchFilterChain
from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Q
from spotseeker_server.require_auth import *
from spotseeker_server.models import Spot, SpotType
from pyproj import Geod
from decimal import *
from time import *
from datetime import datetime
import sys


class SearchView(RESTDispatch):
    """ Handles searching for Spots with particular attributes based on a query string.
    """
    @user_auth_required
    @admin_auth_required
    def POST(self, request):
        return SpotView().run(request)

    @app_auth_required
    def GET(self, request):
        chain = SearchFilterChain(request)
        spots = self.filter_on_request(
            request.GET, chain, request.META, 'spot')

        response = []
        for spot in spots:
            response.append(spot.json_data_structure())

        return JSONResponse(response)

    def distance(self, spot, longitude, latitude):
        g = Geod(ellps='clrk66')
        az12, az21, dist = g.inv(
            spot.longitude, spot.latitude, longitude, latitude)
        return dist

    def get_days_in_range(self, start_day, until_day):
        day_lookup = ["su", "m", "t", "w", "th", "f",
                      "sa", "su", "m", "t", "w", "th", "f", "sa"]
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

    def filter_on_request(self, get_request, chain, request_meta, api):
        form = SpotSearchForm(get_request)
        has_valid_search_param = False

        if not form.is_valid():
            return []

        if len(get_request) == 0:
            # This is here to continue to allow the building api to request all
            # the buildings in the server.
            if api == 'buildings':
                return list(Spot.objects.all())
            return []
        query = Spot.objects.all()

        # This is here to allow only the building api to continue to be
        # contacted with the key 'campus' instead of 'extended_info:campus'
        if api == 'buildings' and 'campus' in get_request.keys():
            query = query.filter(spotextendedinfo__key='campus',
                                 spotextendedinfo__value=get_request['campus'])
            has_valid_search_param = True

        day_dict = {"Sunday": "su",
                    "Monday": "m",
                    "Tuesday": "t",
                    "Wednesday": "w",
                    "Thursday": "th",
                    "Friday": "f",
                    "Saturday": "sa", }
        # Exclude things that get special consideration here, otherwise add a
        # filter for the keys
        for key in get_request:
            if key.startswith('oauth_'):
                pass
            elif key == 'campus':
                pass
            elif chain.filters_key(key):
                # this needs to happen early, before any
                # org_filter or extended_info
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
                if get_request["open_now"]:

                    day_lookup = ["su", "m", "t", "w", "th", "f", "sa"]
                    day_num = int(strftime("%w", localtime()))
                    today = day_lookup[day_num]
                    now = datetime.time(datetime.now())
                    query = query.filter(spotavailablehours__day__iexact=today,
                                         spotavailablehours__start_time__lt=now, spotavailablehours__end_time__gt=now)
                    has_valid_search_param = True
            elif key == "open_until":
                if get_request["open_until"] and get_request["open_at"]:
                    until_day, until_time = get_request[
                        "open_until"].split(',')
                    at_day, at_time = get_request["open_at"].split(',')
                    until_day = day_dict[until_day]
                    at_day = day_dict[at_day]

                    if until_day == at_day:
                        if strptime(until_time, "%H:%M") >= strptime(at_time, "%H:%M"):
                            query = query.filter(spotavailablehours__day__iexact=until_day,
                                                 spotavailablehours__start_time__lte=at_time, spotavailablehours__end_time__gte=until_time)
                        else:
                            days_to_test = ["su", "m",
                                            "t", "w", "th", "f", "sa"]
                            days_to_test.remove(at_day)

                            query = query.filter(spotavailablehours__day__iexact=at_day,
                                                 spotavailablehours__start_time__lte=at_time, spotavailablehours__end_time__gte="23:59")
                            query = query.filter(spotavailablehours__day__iexact=until_day,
                                                 spotavailablehours__start_time__lte="00:00", spotavailablehours__end_time__gte=until_time)

                            for day in days_to_test:
                                query = query.filter(
                                    spotavailablehours__day__iexact=day, spotavailablehours__start_time__lte="00:00", spotavailablehours__end_time__gte="23:59")
                    else:
                        days_to_test = self.get_days_in_range(
                            at_day, until_day)
                        last_day = days_to_test.pop()
                        days_to_test.reverse()
                        first_day = days_to_test.pop()

                        query = query.filter(spotavailablehours__day__iexact=first_day,
                                             spotavailablehours__start_time__lte=at_time, spotavailablehours__end_time__gte="23:59")
                        query = query.filter(spotavailablehours__day__iexact=last_day,
                                             spotavailablehours__start_time__lte="00:00", spotavailablehours__end_time__gte=until_time)

                        for day in days_to_test:
                            query = query.filter(
                                spotavailablehours__day__iexact=day, spotavailablehours__start_time__lte="00:00", spotavailablehours__end_time__gte="23:59")
                    has_valid_search_param = True
            elif key == "open_at":
                if get_request["open_at"]:
                    try:
                        get_request["open_until"]
                    except:
                        day, time = get_request['open_at'].split(',')
                        day = day_dict[day]
                        query = query.filter(spotavailablehours__day__iexact=day,
                                             spotavailablehours__start_time__lte=time, spotavailablehours__end_time__gt=time)
                        has_valid_search_param = True
            elif key == "fuzzy_hours_end":
                # fuzzy search requires a start and end
                if not "fuzzy_hours_start" in get_request.keys():
                    raise RESTException(
                        "fuzzy_hours_end requires fuzzy_hours_start to be specified", 400)
            elif key == "fuzzy_hours_start":
                # fuzzy search requires a start and end
                if not "fuzzy_hours_end" in get_request.keys():
                    raise RESTException(
                        "fuzzy_hours_start requires fuzzy_hours_end to be specified", 400)

                start_day, start_time = get_request[
                    'fuzzy_hours_start'].split(',')
                end_day, end_time = get_request['fuzzy_hours_end'].split(',')
                start_day = day_dict[start_day]
                end_day = day_dict[end_day]

                start_range_query = Q(spotavailablehours__day__iexact=start_day,
                                      spotavailablehours__start_time__gt=start_time, spotavailablehours__start_time__lt=end_time)
                end_range_query = Q(spotavailablehours__day__iexact=end_day,
                                    spotavailablehours__end_time__gt=start_time, spotavailablehours__end_time__lt=end_time)
                span_range_query = Q(spotavailablehours__day__iexact=end_day,
                                     spotavailablehours__start_time__lt=start_time, spotavailablehours__end_time__gt=end_time)
                range_query = (start_range_query |
                               end_range_query | span_range_query)
                query = query.filter(range_query)
                has_valid_search_param = True
            elif key == "capacity":
                try:
                    limit = int(get_request["capacity"])
                    with_limit = Q(capacity__gte=limit)
                    with_limit |= Q(capacity__isnull=True)
                    query = query.filter(with_limit)
                    has_valid_search_param = True
                except ValueError:
                    # This we don't care about - if someone passes "", or
                    # "twenty", just ignore it
                    pass
                except Exception as e:
                    # Do something to complain??
                    pass
            elif key == "type":
                type_values = get_request.getlist(key)
                q_obj = Q()
                type_qs = [Q(spottypes__name__exact=v) for v in type_values]
                for type_q in type_qs:
                    q_obj |= type_q
                query = query.filter(q_obj).distinct()
                has_valid_search_param = True
            elif key == "building_name":
                building_names = get_request.getlist(key)
                q_obj = Q()
                type_qs = [Q(building_name__exact=v) for v in building_names]
                for type_q in type_qs:
                    q_obj |= type_q
                query = query.filter(q_obj).distinct()
                has_valid_search_param = True
            elif key.startswith('extended_info:'):
                kwargs = {
                    'spotextendedinfo__key': key[14:],
                    'spotextendedinfo__value__in': get_request.getlist(key)
                }
                query = query.filter(**kwargs)
                has_valid_search_param = True
            elif key == "id":
                query = query.filter(id__in=get_request.getlist(key))
                has_valid_search_param = True
            else:
                try:
                    kwargs = {
                        '%s__icontains' % key: get_request[key]
                    }
                    query = query.filter(**kwargs)
                    has_valid_search_param = True
                except Exception as e:
                    if not request_meta['SERVER_NAME'] == 'testserver':
                        print >> sys.stderr, "E: ", e

        # Always prefetch the related extended info
        query = query.select_related('SpotExtendedInfo')

        query = chain.filter_query(query)
        if chain.has_valid_search_param:
            has_valid_search_param = True

        limit = 20
        if 'limit' in get_request:
            if get_request['limit'] == '0':
                limit = 0
            else:
                limit = int(get_request['limit'])

        if 'distance' in get_request and 'center_longitude' in get_request and 'center_latitude' in get_request:
            try:
                g = Geod(ellps='clrk66')
                top = g.fwd(get_request['center_longitude'], get_request[
                            'center_latitude'], 0, get_request['distance'])
                right = g.fwd(get_request['center_longitude'], get_request[
                              'center_latitude'], 90, get_request['distance'])
                bottom = g.fwd(get_request['center_longitude'], get_request[
                               'center_latitude'], 180, get_request['distance'])
                left = g.fwd(get_request['center_longitude'], get_request[
                             'center_latitude'], 270, get_request['distance'])

                top_limit = "%.8f" % top[1]
                bottom_limit = "%.8f" % bottom[1]
                left_limit = "%.8f" % left[0]
                right_limit = "%.8f" % right[0]

                distance_query = query.filter(longitude__gte=left_limit)

                distance_query = distance_query.filter(
                    longitude__lte=right_limit)
                distance_query = distance_query.filter(
                    latitude__gte=bottom_limit)
                distance_query = distance_query.filter(latitude__lte=top_limit)
                has_valid_search_param = True

                if len(distance_query) > 0 or 'expand_radius' not in get_request:
                    query = distance_query
                else:
                    # If we're querying everything, let's make sure we only
                    # return a limited number of spaces...
                    limit = 10
            except Exception as e:
                if not request_meta['SERVER_NAME'] == 'testserver':
                    print >> sys.stderr, "E: ", e
                #query = Spot.objects.all()
        elif 'distance' in get_request or 'center_longitude' in get_request or 'center_latitude' in get_request:
            if 'distance' not in get_request or 'center_longitude' not in get_request or 'center_latitude' not in get_request:
                # If distance, lat, or long are specified in the server
                # request; all 3 must be present.
                raise RESTException(
                    "Must specify latitude, longitude, and distance", 400)

        # Only do this if spot api because buildings api
        # is able to not pass any valid filters
        if not has_valid_search_param and api == 'spot':
            return []

        # Do this when spot api because building api is not required
        # to pass these parameters
        if limit > 0 and limit < len(query) and api == 'spot':
            sorted_list = list(query)
            try:
                sorted_list.sort(lambda x, y: cmp(self.distance(x, get_request['center_longitude'], get_request[
                                 'center_latitude']), self.distance(y, get_request['center_longitude'], get_request['center_latitude'])))
                query = sorted_list[:limit]
            except KeyError:
                raise RESTException(
                    "missing required parameters for this type of search", 400)

        spots = set(query)
        spots = chain.filter_results(spots)

        return spots
