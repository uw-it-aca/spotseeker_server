""" Copyright 2013 Board of Trustees, University of Illinois

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

import django.dispatch

# Called in REST after deserializing the JSON but before spot_pre_save.
spot_pre_build = django.dispatch.Signal(
    providing_args=[
        "request",  # HttpRequest
        "json_values",  # Deserialized JSON body
        "spot",  # Spot being operated on
        "stash",  # General stash
        "partial_update",  # If this is a partial update of the spot or not
    ]
)

# Called in REST immediately before saving, after building.
# Extended info and available hours are removed from the body in one of
# these hooks.
spot_pre_save = django.dispatch.Signal(
    providing_args=[
        "request",  # HttpRequest
        "json_values",  # Deserialized JSON body
        "spot",  # Spot being operated on
        "stash",  # General stash
        "partial_update",  # If this is a partial update of the spot or not
    ]
)

# Called in REST after saving, after building the response, but before
# returning it.
spot_post_build = django.dispatch.Signal(
    providing_args=[
        "request",  # HttpRequest
        "response",  # HttpResponse
        "spot",  # Spot being operated on
        "stash",  # General stash
        "partial_update",  # If this is a partial update of the spot or not
    ]
)

# Called in REST immediately after saving, but before building the response.
# Extended info and available hours are processed here and saved to the
# database.
spot_post_save = django.dispatch.Signal(
    providing_args=[
        "request",  # HttpRequest
        "spot",  # Spot being operated on
        "stash",  # General stash
        "partial_update",  # If this is a partial update of the spot or not
    ]
)
