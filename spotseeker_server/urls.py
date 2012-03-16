from django.conf.urls.defaults import patterns, include, url
from spotseeker_server.views.spot import SpotView
from spotseeker_server.views.search import SearchView
from spotseeker_server.views.add_image import AddImageView
from spotseeker_server.views.image import ImageView
from spotseeker_server.views.thumbnail import ThumbnailView

urlpatterns = patterns('',
    url(r'v1/spot/(?P<spot_id>\d+)$', SpotView().run),
    url(r'v1/spot/?$', SearchView().run),
    url(r'v1/spot/(?P<spot_id>\d+)/image$', AddImageView().run),
    url(r'v1/spot/(?P<spot_id>\d+)/image/(?P<image_id>\d+)$', ImageView().run),
    url(r'v1/spot/(?P<spot_id>\d+)/image/(?P<image_id>\d+)/thumb/(?P<thumb_width>\d+)x(?P<thumb_height>\d+)$', ThumbnailView().run),
)
