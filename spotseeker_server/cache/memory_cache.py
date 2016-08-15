"""A cache that stores spot JSON representations in memory for fast loading"""
from spotseeker_server.models import Spot


spots_cache = {}


def get_spot(spot_model):
    """Retrieves the cached version of the spot with the provided ID."""
    verify_cache(spot_model)

    return spots_cache[spot_model.id]


def get_spots(spots):
    """Retrieves a list of spots from the cache."""
    if not spots_cache:
        load_spots()

    spot_dicts = []
    for spot in spots:
        verify_cache(spot)
        spot_json = spots_cache[spot.id]
        spot_dicts.append(spot_json)

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
        spots_cache[spot.id] = spot.json_data_structure()


def cache_spot(spot_model):
    """Sets the cache of a spot."""
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
    if spots_cache[spot_model.id]['etag'] != spot_model.etag:
        cache_spot(spot_model)
