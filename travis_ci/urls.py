from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin

urlpatterns = patterns('',
    url(r'^auth/', include('oauth_provider.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/', include('spotseeker_server.urls')),
)

urlpatterns += staticfiles_urlpatterns()
