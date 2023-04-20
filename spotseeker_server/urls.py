# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.urls import path, re_path, include
from django.views.decorators.csrf import csrf_exempt
from spotseeker_server.views.buildings import BuildingListView
from spotseeker_server.views.spot import SpotView
from spotseeker_server.views.search import SearchView
from spotseeker_server.views.add_image import AddImageView
from spotseeker_server.views.image import ImageView
from spotseeker_server.views.thumbnail import ThumbnailView
from spotseeker_server.views.null import NullView
from spotseeker_server.views.all_spots import AllSpotsView
from spotseeker_server.views.schema_gen import SchemaGenView
from spotseeker_server.views.person import PersonView
from spotseeker_server.views.item_image import ItemImageView
from spotseeker_server.views.add_item_image import AddItemImageView
from spotseeker_server.views.item_thumbnail import ItemThumbnailView

urlpatterns = [
    path("v1/null", csrf_exempt(NullView().run)),
    re_path(
        r"v1/spot/(?P<spot_id>(\d+|external:[\w-]+))$",
        csrf_exempt(SpotView().run),
        name="spot",
    ),
    re_path(r"v1/spot/?$", csrf_exempt(SearchView().run), name="spot-search"),
    path("v1/spot/all", csrf_exempt(AllSpotsView().run), name="spots"),
    re_path(
        r"v1/buildings/?$",
        csrf_exempt(BuildingListView().run),
        name="buildings",
    ),
    path("v1/schema", csrf_exempt(SchemaGenView().run), name="schema"),
    path(r"v1/spot/<int:spot_id>/image", csrf_exempt(AddImageView().run)),
    path(
        "v1/spot/<int:spot_id>/image/<int:image_id>",
        csrf_exempt(ImageView().run),
        name="spot-image",
    ),
    re_path(
        r"v1/spot/(?P<spot_id>\d+)/image/"
        r"(?P<image_id>\d+)/thumb/constrain/"
        "(?P<thumb_dimensions>.+)?$",
        csrf_exempt(ThumbnailView().run),
        {"constrain": True},
    ),
    re_path(
        r"v1/spot/(?P<spot_id>\d+)/image/"
        r"(?P<image_id>\d+)/thumb/"
        r"(?P<thumb_dimensions>.+)?$",
        csrf_exempt(ThumbnailView().run),
        name="spot-image-thumb",
    ),
    re_path(
        r"v1/item/(?P<item_id>\d+)/image$", csrf_exempt(AddItemImageView().run)
    ),
    re_path(
        r"v1/item/(?P<item_id>\d+)/image/" r"(?P<image_id>[\d]+)$",
        csrf_exempt(ItemImageView().run),
        name="item-image",
    ),
    re_path(
        r"v1/item/(?P<item_id>\d+)/image/"
        r"(?P<image_id>\d+)/thumb/constrain/"
        r"(?P<thumb_dimensions>.+)?$",
        csrf_exempt(ItemThumbnailView().run),
        {"constrain": True},
    ),
    re_path(
        r"v1/item/(?P<item_id>\d+)/image/"
        r"(?P<image_id>\d+)/thumb/"
        r"(?P<thumb_dimensions>.+)?$",
        csrf_exempt(ItemThumbnailView().run),
        name="item-image-thumb",
    ),
    re_path(r"v1/user/me$", csrf_exempt(PersonView().run)),
]
