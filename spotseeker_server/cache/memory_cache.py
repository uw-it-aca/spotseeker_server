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
from spotseeker_server.models import Spot
from django.conf import settings
from collections import OrderedDict
from sys import maxint

spots_cache = OrderedDict()
spot_cache_limit = getattr(settings, 'SPOTSEEKER_SPOT_CACHE_LIMIT', maxint)


def get_spot(spot_model):
    """Retrieves the cached version of the spot with the provided ID."""
    verify_cache(spot_model)

    if spot_model.id in spots_cache:
        spot_json = spots_cache[spot_model.id]
    else:
        spot_json = spot_model.json_data_structure()

    return spot_json


def get_spots(spots):
    """Retrieves a list of spots from the cache."""
    if not spots_cache:
        load_spots()

    spot_dicts = [get_spot(spot) for spot in spots]

    return spot_dicts


def get_all_spots():
    """Returns all spots stored in the cache."""
    return get_spots(Spot.objects.all())
    # return spots_cache.values()


def load_spots():
    """
    Loads all spots from the database and stores their JSON representations in
    the memory cache.
    """
    spots = Spot.objects.all()
    for spot in spots:
        if len(spots_cache.keys()) > spot_cache_limit:
            break
        spots_cache[spot.id] = spot.json_data_structure()


def cache_spot(spot_model):
    """Sets the cache of a spot."""
    if len(spots_cache.keys()) > spot_cache_limit:
        spots_cache.popitem(last=False)

    spots_cache[spot_model.id] = spot_model.json_data_structure()


def delete_spot(spot_model):
    """Removes a specific spot from the cache"""
    if spot_model.id in spots_cache:
        del spots_cache[spot_model.id]


def clear_cache():
    """Clears the cache."""
    spots_cache.clear()


def verify_cache(spot_model):
    """Ensures a given spot model is in the cache and up to date"""
    is_in_cache(spot_model)

    verify_etag(spot_model)


def is_in_cache(spot_model):
    """Checks if a spot model is in the cache, and caches it if not."""
    if spot_model.id not in spots_cache:
        cache_spot(spot_model)


def verify_etag(spot_model):
    """Checks the model etag against the cache, updates if out of date."""
    if (spot_model.id in spots_cache and
            spots_cache[spot_model.id]['etag'] != spot_model.etag):
        cache_spot(spot_model)
