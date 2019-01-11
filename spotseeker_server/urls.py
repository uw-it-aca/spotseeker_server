""" Copyright 2012-2014 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Changes
    =================================================================

    sbutler1@illinois.edu: added external_id support; moved some URL
        patterns into the ThumbnailView; added names for reverse()
        support.
"""

from django.conf.urls import patterns, include, url
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
from spotseeker_server.views.share_space import \
    ShareSpaceView, SharedSpaceReferenceView
from spotseeker_server.views.reviews import ReviewsView, UnpublishedReviewsView
from spotseeker_server.views.item_image import ItemImageView
from spotseeker_server.views.add_item_image import AddItemImageView
from spotseeker_server.views.item_thumbnail import ItemThumbnailView

urlpatterns = patterns('',
                       url(r'v1/null$', csrf_exempt(NullView().run)),
                       url(r'v1/spot/(?P<spot_id>([0-9]+|external:[\w-]+))$',
                           csrf_exempt(SpotView().run), name='spot'),
                       url(r'v1/spot/?$',
                           csrf_exempt(SearchView().run),
                           name='spot-search'),
                       url(r'v1/spot/all$',
                           csrf_exempt(AllSpotsView().run),
                           name='spots'),
                       url(r'v1/buildings/?$',
                           csrf_exempt(BuildingListView().run),
                           name='buildings'),
                       url(r'v1/schema$',
                           csrf_exempt(SchemaGenView().run),
                           name='schema'),
                       url(r'v1/spot/(?P<spot_id>[0-9]+)/image$',
                           csrf_exempt(AddImageView().run)),
                       url(r'v1/spot/(?P<spot_id>[0-9]+)/image/'
                           '(?P<image_id>[0-9]+)$',
                           csrf_exempt(ImageView().run),
                           name='spot-image'),
                       url(r'v1/spot/(?P<spot_id>[0-9]+)/image/'
                           '(?P<image_id>[0-9]+)/thumb/constrain/'
                           '(?P<thumb_dimensions>.+)?$',
                           csrf_exempt(ThumbnailView().run),
                           {'constrain': True}),
                       url(r'v1/spot/(?P<spot_id>[0-9]+)/image/'
                           '(?P<image_id>[0-9]+)/thumb/'
                           '(?P<thumb_dimensions>.+)?$',
                           csrf_exempt(ThumbnailView().run),
                           name='spot-image-thumb'),
                       url(r'v1/item/(?P<item_id>[0-9]+)/image$',
                           csrf_exempt(AddItemImageView().run)),
                       url(r'v1/item/(?P<item_id>[0-9]+)/image/'
                           '(?P<image_id>[0-9]+)$',
                           csrf_exempt(ItemImageView().run),
                           name='item-image'),
                       url(r'v1/item/(?P<item_id>[0-9]+)/image/'
                           '(?P<image_id>[0-9]+)/thumb/constrain/'
                           '(?P<thumb_dimensions>.+)?$',
                           csrf_exempt(ItemThumbnailView().run),
                           {'constrain': True}),
                       url(r'v1/item/(?P<item_id>[0-9]+)/image/'
                           '(?P<image_id>[0-9]+)/thumb/'
                           '(?P<thumb_dimensions>.+)?$',
                           csrf_exempt(ItemThumbnailView().run),
                           name='item-image-thumb'),
                       url(r'v1/spot/(?P<spot_id>[0-9]+)/reviews$',
                           csrf_exempt(ReviewsView().run)),
                       url(r'v1/user/me/favorites/?$',
                           csrf_exempt(FavoritesView().run)),
                       url(r'v1/user/me$',
                           csrf_exempt(PersonView().run)),
                       url(r'v1/user/me/favorite/(?P<spot_id>[0-9]+)$',
                           csrf_exempt(FavoritesView().run)),
                       url(r'v1/spot/(?P<spot_id>[0-9]+)/share$',
                           csrf_exempt(ShareSpaceView().run)),
                       url(r'v1/spot/(?P<spot_id>[0-9]+)/shared$',
                           csrf_exempt(SharedSpaceReferenceView().run)),
                       url(r'v1/reviews/unpublished$',
                           csrf_exempt(UnpublishedReviewsView().run)),
                       )
