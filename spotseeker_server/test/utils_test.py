# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""Provide useful methods for testing

This module contains useful methods that can be reused by various tests.
"""


def get_item():
    """Returns a dict representing an item."""
    return {
         'name': 'Nikon D3100 14.2 MP',
         'category': 'Cameras',
         'subcategory': 'Nikon Cameras',
         'extended_info': {}
     }


def get_spot(spot_name, capacity):
    """Returns a dict representing a spot."""
    return {
        'name': spot_name,
        'capacity': capacity,
        'location': {'latitude': 50, 'longitude': -30},
        'items': [],
        'extended_info': {}
    }
