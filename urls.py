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

    Changes
    =================================================================

    sbutler1@illinois.edu: added external_id support; moved some URL
        patterns into the ThumbnailView; added names for reverse()
        support.
"""

from django.conf.urls.defaults import patterns, include, url
from spotseeker_server.views.buildings import BuildingListView
from spotseeker_server.views.spot import SpotView
from spotseeker_server.views.search import SearchView
from spotseeker_server.views.add_image import AddImageView
from spotseeker_server.views.image import ImageView
from spotseeker_server.views.thumbnail import ThumbnailView
from spotseeker_server.views.null import NullView
from spotseeker_server.views.all_spots import AllSpotsView
from spotseeker_server.views.schema_gen import SchemaGenView

urlpatterns = patterns('',
    url(r'v1/null$', NullView().run),
    url(r'v1/spot/(?P<spot_id>(\d+|external:[\w-]+))$', SpotView().run, name='spot'),
    url(r'v1/spot/?$', SearchView().run, name='spot-search'),
    url(r'v1/spot/all$', AllSpotsView().run, name='spots'),
    url(r'v1/buildings/?$', BuildingListView().run, name='buildings'),
    url(r'v1/schema$', SchemaGenView().run, name='schema'),
    url(r'v1/spot/(?P<spot_id>\d+)/image$', AddImageView().run),
    url(r'v1/spot/(?P<spot_id>\d+)/image/(?P<image_id>\d+)$', ImageView().run, name='spot-image'),
    url(r'v1/spot/(?P<spot_id>\d+)/image/(?P<image_id>\d+)/thumb/constrain/(?P<thumb_dimensions>.+)?$', ThumbnailView().run, {'constrain': True}),
    url(r'v1/spot/(?P<spot_id>\d+)/image/(?P<image_id>\d+)/thumb/(?P<thumb_dimensions>.+)?$', ThumbnailView().run, name='spot-image-thumb'),
)
