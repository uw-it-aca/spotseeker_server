# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" Changes
    =================================================================

    sbutler1@illinois.edu: adapt to the new RESTDispatch framework;
        remove some needless use of regex; add open_anytime option;
        move some UW options into new org_filter; add org_filter
        support (hooks).
"""
from __future__ import print_function

from spotseeker_server.views.rest_dispatch import (
    RESTDispatch,
    RESTException,
    JSONResponse,
)
from spotseeker_server.forms.spot_search import SpotSearchForm
from spotseeker_server.views.spot import SpotView
from spotseeker_server.org_filters import SearchFilterChain
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Q
from django.utils.datastructures import MultiValueDictKeyError
from spotseeker_server.require_auth import *
from spotseeker_server.models import Spot, SpotType
from pyproj import Geod
from decimal import *
from time import *
from datetime import datetime
import pytz
import sys


class SearchView(RESTDispatch):
    """Handles searching for Spots with particular attributes
    based on a query string.
    """

    @user_auth_required
    @admin_auth_required
    def POST(self, request):
        return SpotView().run(request)

    @app_auth_required
    def GET(self, request):
        chain = SearchFilterChain(request)
        spots = self.filter_on_request(
            request.GET, chain, request.META, "spot"
        )

        response = []
        for spot in spots:
            response.append(spot.json_data_structure())

        return JSONResponse(response)

    def distance(self, spot, longitude, latitude):
        g = Geod(ellps="clrk66")
        az12, az21, dist = g.inv(
            spot.longitude, spot.latitude, longitude, latitude
        )
        return dist

    def get_days_in_range(self, start_day, until_day):
        day_lookup = [
            "su",
            "m",
            "t",
            "w",
            "th",
            "f",
            "sa",
            "su",
            "m",
            "t",
            "w",
            "th",
            "f",
            "sa",
        ]
        starting = day_lookup[day_lookup.index(start_day):]
        matched_days = starting[: starting.index(until_day) + 1]
        return matched_days

    def filter_on_request(self, get_request, chain, request_meta, api):
        form = SpotSearchForm(get_request)
        has_valid_search_param = False

        if not form.is_valid():
            return []

        if not get_request:
            # This is here to continue to allow the building api to request all
            # the buildings in the server.
            if api == "buildings":
                return list(Spot.objects.all())
            return []
        query = Spot.objects.all()

        # This is here to allow only the building api to continue to be
        # contacted with the key 'campus' instead of 'extended_info:campus'
        if api == "buildings" and "campus" in get_request.keys():
            query = query.filter(
                spotextendedinfo__key="campus",
                spotextendedinfo__value=get_request["campus"],
            )
            has_valid_search_param = True

        day_dict = {
            "Sunday": "su",
            "Monday": "m",
            "Tuesday": "t",
            "Wednesday": "w",
            "Thursday": "th",
            "Friday": "f",
            "Saturday": "sa",
        }

        # Q objects we need to chain together for the OR queries
        or_q_obj = Q()
        or_qs = []

        # Exclude things that get special consideration here, otherwise add a
        # filter for the keys
        for key in get_request:
            if key.startswith("oauth_"):
                pass
            elif key == "campus":
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
                    today, now = self.get_datetime()
                    # Check to see if the request was made in minute
                    # gap before midnight during which no space is open,
                    # based on the server.
                    before_midnight = now.replace(
                        hour=23, minute=58, second=59, microsecond=999999
                    )
                    right_before_midnight = now.replace(
                        hour=23, minute=59, second=59, microsecond=999999
                    )
                    if before_midnight < now and now < right_before_midnight:
                        # Makes it so that all spaces that are open
                        # until midnight or overnight will be returned.
                        now = now.replace(
                            hour=23, minute=58, second=0, microsecond=0
                        )
                    query = query.filter(
                        spotavailablehours__day__iexact=today,
                        spotavailablehours__start_time__lt=now,
                        spotavailablehours__end_time__gt=now,
                    )
                    has_valid_search_param = True
            elif key == "open_until":
                if get_request["open_until"] and get_request["open_at"]:
                    until_day, until_t = get_request["open_until"].split(",")
                    at_day, at_t = get_request["open_at"].split(",")
                    until_day = day_dict[until_day]
                    at_day = day_dict[at_day]

                    if until_day == at_day:
                        if strptime(until_t, "%H:%M") >= strptime(
                            at_t, "%H:%M"
                        ):
                            query = query.filter(
                                spotavailablehours__day__iexact=until_day,
                                spotavailablehours__start_time__lte=at_t,
                                spotavailablehours__end_time__gte=until_t,
                            )
                        else:
                            days_to_test = [
                                "su",
                                "m",
                                "t",
                                "w",
                                "th",
                                "f",
                                "sa",
                            ]
                            days_to_test.remove(at_day)

                            query = query.filter(
                                spotavailablehours__day__iexact=at_day,
                                spotavailablehours__start_time__lte=at_t,
                                spotavailablehours__end_time__gte="23:59",
                            )
                            t1 = "00:00"
                            query = query.filter(
                                spotavailablehours__day__iexact=until_day,
                                spotavailablehours__start_time__lte=t1,
                                spotavailablehours__end_time__gte=until_t,
                            )

                            for day in days_to_test:
                                t1 = "00:00"
                                t2 = "23:59"
                                query = query.filter(
                                    spotavailablehours__day__iexact=day,
                                    spotavailablehours__start_time__lte=t1,
                                    spotavailablehours__end_time__gte=t2,
                                )
                    else:
                        days_to_test = self.get_days_in_range(
                            at_day, until_day
                        )
                        last_day = days_to_test.pop()
                        days_to_test.reverse()
                        first_day = days_to_test.pop()

                        query = query.filter(
                            spotavailablehours__day__iexact=first_day,
                            spotavailablehours__start_time__lte=at_t,
                            spotavailablehours__end_time__gte="23:59",
                        )
                        query = query.filter(
                            spotavailablehours__day__iexact=last_day,
                            spotavailablehours__start_time__lte="00:00",
                            spotavailablehours__end_time__gte=until_t,
                        )

                        for day in days_to_test:
                            early = "00:00"
                            query = query.filter(
                                spotavailablehours__day__iexact=day,
                                spotavailablehours__start_time__lte=early,
                                spotavailablehours__end_time__gte="23:59",
                            )
                    has_valid_search_param = True
            elif key == "open_at":
                if get_request["open_at"]:
                    try:
                        get_request["open_until"]
                    except MultiValueDictKeyError:
                        day, time = get_request["open_at"].split(",")
                        day = day_dict[day]
                        query = query.filter(
                            spotavailablehours__day__iexact=day,
                            spotavailablehours__start_time__lte=time,
                            spotavailablehours__end_time__gt=time,
                        )
                        has_valid_search_param = True
            elif key == "fuzzy_hours_end":
                # fuzzy search requires a start and end
                if "fuzzy_hours_start" not in get_request.keys():
                    raise RESTException(
                        "fuzzy_hours_end requires "
                        "fuzzy_hours_start to be specified",
                        400,
                    )
            elif key == "fuzzy_hours_start":
                # fuzzy search requires a start and end
                starts = get_request.getlist("fuzzy_hours_start")
                ends = get_request.getlist("fuzzy_hours_end")
                if "fuzzy_hours_end" not in get_request.keys() or not len(
                    starts
                ) is len(ends):
                    raise RESTException(
                        "fuzzy_hours_start requires "
                        "fuzzy_hours_end to be specified",
                        400,
                    )

                or_small_q_obj = Q()
                for num, start in enumerate(starts):
                    start_day, start_time = start.split(",")
                    end_day, end_time = ends[num].split(",")
                    start_day = day_dict[start_day]
                    end_day = day_dict[end_day]

                    start_range_query = Q(
                        spotavailablehours__day__iexact=start_day,
                        spotavailablehours__start_time__gte=start_time,
                        spotavailablehours__start_time__lt=end_time,
                    )
                    end_range_query = Q(
                        spotavailablehours__day__iexact=end_day,
                        spotavailablehours__end_time__gt=start_time,
                        spotavailablehours__end_time__lte=end_time,
                    )
                    span_range_query = Q(
                        spotavailablehours__day__iexact=end_day,
                        spotavailablehours__start_time__lte=start_time,
                        spotavailablehours__end_time__gt=end_time,
                    )
                    span_midnight_pre_query = Q(
                        spotavailablehours__day__iexact=start_day,
                        spotavailablehours__start_time__gte=start_time,
                        spotavailablehours__start_time__lte="23:59",
                    )
                    span_midnight_post_query = Q(
                        spotavailablehours__day__iexact=end_day,
                        spotavailablehours__end_time__lt=end_time,
                        spotavailablehours__end_time__gte="00:00",
                    )
                    span_midnight_pre_midnight_end_query = Q(
                        spotavailablehours__day__iexact=end_day,
                        spotavailablehours__end_time__gte=start_time,
                        spotavailablehours__end_time__lte="23:59",
                    )
                    span_midnight_next_morning_query = Q(
                        spotavailablehours__day__iexact=end_day,
                        spotavailablehours__start_time__lt=end_time,
                        spotavailablehours__start_time__gte="00:00",
                    )
                    if start_day is not end_day:
                        range_query = (
                            start_range_query
                            | end_range_query
                            | span_midnight_pre_query
                            | span_midnight_post_query
                            | span_midnight_pre_midnight_end_query
                            | span_midnight_next_morning_query
                        )
                    else:
                        range_query = (
                            start_range_query
                            | end_range_query
                            | span_range_query
                        )
                    or_small_q_obj |= range_query
                query = query.filter(or_small_q_obj)
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
            elif key.startswith("item:extended_info:"):
                try:
                    for value in get_request.getlist(key):
                        or_qs.append(
                            Q(
                                item__itemextendedinfo__key=key[19:],
                                item__itemextendedinfo__value=value,
                            )
                        )
                    has_valid_search_param = True
                except Exception as e:
                    pass
            elif key.startswith("item:"):
                try:
                    for value in get_request.getlist(key):
                        if key[5:] == "id":
                            or_qs.append(Q(item__id=value))
                        elif key[5:] == "name":
                            or_qs.append(Q(item__name=value))
                        elif key[5:] == "category":
                            or_qs.append(Q(item__item_category=value))
                        elif key[5:] == "subcategory":
                            or_qs.append(Q(item__item_subcategory=value))
                    has_valid_search_param = True
                except Exception as e:
                    pass
            elif key.startswith("extended_info:or_group"):
                values = get_request.getlist(key)
                or_small_q_obj = Q()
                for value in values:
                    or_small_q_obj |= Q(
                        spotextendedinfo__key=value,
                        spotextendedinfo__value="true",
                    )
                query = query.filter(or_small_q_obj)
                has_valid_search_param = True
            elif key.startswith("extended_info:or"):
                or_qs.append(
                    Q(
                        spotextendedinfo__key=key[17:],
                        spotextendedinfo__value="true",
                    )
                )
                has_valid_search_param = True
            elif key.startswith("extended_info:"):
                kwargs = {
                    "spotextendedinfo__key": key[14:],
                    "spotextendedinfo__value__in": get_request.getlist(key),
                }
                query = query.filter(**kwargs)
                has_valid_search_param = True
            elif key == "id":
                query = query.filter(id__in=get_request.getlist(key))
                has_valid_search_param = True
            else:
                try:
                    kwargs = {"%s__icontains" % key: get_request[key]}
                    query = query.filter(**kwargs)
                    has_valid_search_param = True
                except Exception as e:
                    if not request_meta["SERVER_NAME"] == "testserver":
                        print("E: ", e, file=sys.stderr)

        for or_q in or_qs:
            or_q_obj |= or_q
        # This handles all of the OR queries on extended_info we've collected.
        query = query.filter(or_q_obj).distinct()
        # Always prefetch the related extended info
        query = query.prefetch_related("spotextendedinfo_set")

        query = chain.filter_query(query)
        if chain.has_valid_search_param:
            has_valid_search_param = True

        limit = int(get_request.get("limit", 20))

        if (
            "distance" in get_request
            and "center_longitude" in get_request
            and "center_latitude" in get_request
        ):
            try:
                g = Geod(ellps="clrk66")
                lon = get_request["center_longitude"]
                lat = get_request["center_latitude"]
                dist = get_request["distance"]
                # Get coordinates above/right/below/left our location
                top = g.fwd(lon, lat, 0, dist)
                right = g.fwd(lon, lat, 90, dist)
                bottom = g.fwd(lon, lat, 180, dist)
                left = g.fwd(lon, lat, 270, dist)
                # Get relevant lat or long from these points
                top_limit = "%.8f" % top[1]
                bottom_limit = "%.8f" % bottom[1]
                left_limit = "%.8f" % left[0]
                right_limit = "%.8f" % right[0]

                distance_query = query.filter(
                    longitude__gte=left_limit,
                    longitude__lte=right_limit,
                    latitude__gte=bottom_limit,
                    latitude__lte=top_limit,
                )
                has_valid_search_param = True

                if distance_query or "expand_radius" not in get_request:
                    query = distance_query
                else:
                    # If we're querying everything, let's make sure we only
                    # return a limited number of spaces...
                    limit = 10
            except Exception as e:
                if not request_meta["SERVER_NAME"] == "testserver":
                    print("E: ", e, file=sys.stderr)
                # query = Spot.objects.all()
        elif (
            "distance" in get_request
            or "center_longitude" in get_request
            or "center_latitude" in get_request
        ):
            if (
                "distance" not in get_request
                or "center_longitude" not in get_request
                or "center_latitude" not in get_request
            ):
                # If distance, lat, or long are specified in the server
                # request; all 3 must be present.
                raise RESTException(
                    "Must specify latitude, longitude, and distance", 400
                )

        # Only do this if spot api because buildings api
        # is able to not pass any valid filters
        if not has_valid_search_param and api == "spot":
            raise RESTException(
                "missing required parameters for this type of search", 400
            )

        # Do this when spot api because building api is not required
        # to pass these parameters
        if limit > 0 and limit < len(query) and api == "spot":
            try:
                lat = get_request["center_latitude"]
                lon = get_request["center_longitude"]
            except KeyError:
                raise RESTException(
                    "missing required parameters for this type of search", 400
                )

            def sortfunc(spot):
                return self.distance(spot, lon, lat)

            sorted_list = sorted(query, key=sortfunc)
            query = sorted_list[:limit]

        spots = set(query)
        spots = chain.filter_results(spots)

        return spots

    def get_datetime(self):
        """Returns the datetime and the day of the week."""
        day_lookup = ["su", "m", "t", "w", "th", "f", "sa"]
        day_num = int(strftime("%w", localtime()))
        now = datetime.now(pytz.timezone(
                getattr(settings, 'TIME_ZONE', 'America/Los_Angeles')
            ))
        today = day_lookup[day_num]
        return today, now
