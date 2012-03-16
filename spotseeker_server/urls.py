from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('spotseeker_server.views',
    url(r'v1/spot/(?P<spot_id>\d+)$', 'spot'),
    url(r'v1/spot$', 'search'),
    url(r'v1/spot/(?P<spot_id>\d+)/image$', 'add_image'),
    url(r'v1/spot/(?P<spot_id>\d+)/image/(?P<image_id>\d+)$', 'view_image'),
    url(r'v1/spot/(?P<spot_id>\d+)/image/(?P<image_id>\d+)/thumb/(?P<thumb_width>\d+)x(?P<thumb_height>\d+)$', 'view_thumbnail'),
)
