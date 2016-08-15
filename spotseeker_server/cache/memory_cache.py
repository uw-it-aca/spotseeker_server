"""A cache that stores spot JSON representations in memory for fast loading"""
from spotseeker_server.models import Spot


spots_cache = {}


def get_spot(spot_id):
    """Retrieves the cached version of the spot with the provided ID."""
    # TODO : modify to take spot model
    if spot_id not in spots_cache:
        spot_model = Spot.objects.get(id=spot_id)
        cache_spot(spot_model)

    return spots_cache[spot_id]


def get_spots(spots):
    """Retrieves a list of spots from the cache."""
    if not spots_cache:
        load_spots()

    spot_dicts = []
    for spot in spots:
        if spot.id not in spots_cache:
            cache_spot(spot)
        spot_json = spots_cache[spot.id]
        # update the spot if the etags do not match
        if spot_json['etag'] != spot.etag:
            cache_spot(spot)

        spot_dicts.append(spot_json)

    return spot_dicts


def get_all_spots():
    """Returns all spots stored in the cache."""
    return spots_cache.values()


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
