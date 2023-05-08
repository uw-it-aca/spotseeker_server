# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('api/', include('spotseeker_server.urls')),
    path(
        'auth/',
        include('oauth2_provider.urls', namespace='oauth2_provider')
    ),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += [
        path('admin/doc/', include('django.contrib.admindocs.urls')),
        path('admin/', admin.site.urls),
    ]

    urlpatterns += staticfiles_urlpatterns()
