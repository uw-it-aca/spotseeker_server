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
from sys import maxint

spots_cache = {}
spots_entries = []
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
        if len(spots_cache) > spot_cache_limit:
            break
        set_cache_entry(spot)


def delete_oldest():
    """Delete the oldest spot from the cache"""
    if spot_entries:
        spot_id = spots_entries.pop(0)
        del spots_cache[spot_id]


def cache_spot(spot_model):
    """Sets the cache of a spot."""
    if len(spots_cache.keys()) > spot_cache_limit:
        delete_oldest()
    set_cache_entry(spot_model)


def set_cache_entry(spot_model):
    """Do nothing but set a cache entry and update order"""
    spots_cache[spot_model.id] = spot_model.json_data_structure()
    update_position(spot_model)


def update_position(spot_model):
    """Bump a spot to beginning of queue"""
    spot_id = spot_model.id
    try:
        spots_entries.remove(spot_id)
    except ValueError:
        pass
    spots_entries.append(spot_id)


def delete_spot(spot_model):
    """Removes a specific spot from the cache"""
    if spot_model.id in spots_cache:
        del spots_cache[spot_model.id]


def clear_cache():
    """Clears the cache."""
    spots_cache.clear()
    global spots_entries
    spots_entries = []


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
