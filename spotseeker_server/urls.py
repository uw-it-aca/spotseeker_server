# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" Changes
    =================================================================

    sbutler1@illinois.edu: added external_id support; moved some URL
        patterns into the ThumbnailView; added names for reverse()
        support.
"""

from django.conf.urls import include, url
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
from spotseeker_server.views.favorites import FavoritesView
from spotseeker_server.views.person import PersonView
from spotseeker_server.views.share_space import (
    ShareSpaceView,
    SharedSpaceReferenceView,
)
from spotseeker_server.views.reviews import ReviewsView, UnpublishedReviewsView
from spotseeker_server.views.item_image import ItemImageView
from spotseeker_server.views.add_item_image import AddItemImageView
from spotseeker_server.views.item_thumbnail import ItemThumbnailView

urlpatterns = [
    url(r"v1/null$", csrf_exempt(NullView().run)),
    url(
        r"v1/spot/(?P<spot_id>(\d+|external:[\w-]+))$",
        csrf_exempt(SpotView().run),
        name="spot",
    ),
    url(r"v1/spot/?$", csrf_exempt(SearchView().run), name="spot-search"),
    url(r"v1/spot/all$", csrf_exempt(AllSpotsView().run), name="spots"),
    url(
        r"v1/buildings/?$",
        csrf_exempt(BuildingListView().run),
        name="buildings",
    ),
    url(r"v1/schema$", csrf_exempt(SchemaGenView().run), name="schema"),
    url(r"v1/spot/(?P<spot_id>\d+)/image$", csrf_exempt(AddImageView().run)),
    url(
        r"v1/spot/(?P<spot_id>\d+)/image/" r"(?P<image_id>\d+)$",
        csrf_exempt(ImageView().run),
        name="spot-image",
    ),
    url(
        r"v1/spot/(?P<spot_id>\d+)/image/"
        r"(?P<image_id>\d+)/thumb/constrain/"
        "(?P<thumb_dimensions>.+)?$",
        csrf_exempt(ThumbnailView().run),
        {"constrain": True},
    ),
    url(
        r"v1/spot/(?P<spot_id>\d+)/image/"
        r"(?P<image_id>\d+)/thumb/"
        r"(?P<thumb_dimensions>.+)?$",
        csrf_exempt(ThumbnailView().run),
        name="spot-image-thumb",
    ),
    url(
        r"v1/item/(?P<item_id>\d+)/image$", csrf_exempt(AddItemImageView().run)
    ),
    url(
        r"v1/item/(?P<item_id>\d+)/image/" r"(?P<image_id>[\d]+)$",
        csrf_exempt(ItemImageView().run),
        name="item-image",
    ),
    url(
        r"v1/item/(?P<item_id>\d+)/image/"
        r"(?P<image_id>\d+)/thumb/constrain/"
        r"(?P<thumb_dimensions>.+)?$",
        csrf_exempt(ItemThumbnailView().run),
        {"constrain": True},
    ),
    url(
        r"v1/item/(?P<item_id>\d+)/image/"
        r"(?P<image_id>\d+)/thumb/"
        r"(?P<thumb_dimensions>.+)?$",
        csrf_exempt(ItemThumbnailView().run),
        name="item-image-thumb",
    ),
    url(r"v1/spot/(?P<spot_id>\d+)/reviews$", csrf_exempt(ReviewsView().run)),
    url(r"v1/user/me/favorites/?$", csrf_exempt(FavoritesView().run)),
    url(r"v1/user/me$", csrf_exempt(PersonView().run)),
    url(
        r"v1/user/me/favorite/(?P<spot_id>\d+)$",
        csrf_exempt(FavoritesView().run),
    ),
    url(r"v1/spot/(?P<spot_id>\d+)/share$", csrf_exempt(ShareSpaceView().run)),
    url(
        r"v1/spot/(?P<spot_id>\d+)/shared$",
        csrf_exempt(SharedSpaceReferenceView().run),
    ),
    url(r"v1/reviews/unpublished$", csrf_exempt(UnpublishedReviewsView().run)),
]
