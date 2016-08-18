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


def get_spot(spot_model):
    """Retrieves the json of the spot with the provided ID."""
    return spot_model.json_data_structure()


def get_spots(spots):
    """Retrieves a list of spots from the backend."""
    return [get_spot(spot) for spot in spots]


def get_all_spots():
    """ Retrieves a list of JSON representations of all spots"""
    spots = Spot.objects.all()
    return [get_spot(spot) for spot in spots]


def cache_spot(spot):
    pass


def delete_spot(spot):
    pass


def clear_cache():
    pass
