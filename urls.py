from django.conf.urls.defaults import patterns, include, url
from spotseeker_server.views.buildings import BuildingListView
from spotseeker_server.views.spot import SpotView
from spotseeker_server.views.search import SearchView
from spotseeker_server.views.add_image import AddImageView
from spotseeker_server.views.image import ImageView
from spotseeker_server.views.thumbnail import ThumbnailView
from spotseeker_server.views.null import NullView
from spotseeker_server.views.all_spots import AllSpotsView

urlpatterns = patterns('',
    url(r'v1/null$', NullView().run),
    url(r'v1/spot/(?P<spot_id>\d+)$', SpotView().run),
    url(r'v1/spot/?$', SearchView().run),
    url(r'v1/spot/all$', AllSpotsView().run),
    url(r'v1/buildings/?$', BuildingListView().run),
    url(r'v1/schema$', 'spotseeker_server.views.schema_gen.schema_gen'),
    url(r'v1/spot/(?P<spot_id>\d+)/image$', AddImageView().run),
    url(r'v1/spot/(?P<spot_id>\d+)/image/(?P<image_id>\d+)$', ImageView().run),
    url(r'v1/spot/(?P<spot_id>\d+)/image/(?P<image_id>\d+)/thumb/constrain/width:(?P<thumb_width>\d+)(?:,height:(?P<thumb_height>\d+))?$', ThumbnailView().run, {'constrain': True}),
    url(r'v1/spot/(?P<spot_id>\d+)/image/(?P<image_id>\d+)/thumb/constrain/height:(?P<thumb_height>\d+)(?:,width:(?P<thumb_width>\d+))?$', ThumbnailView().run, {'constrain': True}),
    url(r'v1/spot/(?P<spot_id>\d+)/image/(?P<image_id>\d+)/thumb/(?P<thumb_width>\d+)x(?P<thumb_height>\d+)$', ThumbnailView().run),
)
