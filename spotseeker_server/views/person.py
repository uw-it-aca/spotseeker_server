# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from spotseeker_server.views.rest_dispatch import RESTDispatch, JSONResponse
from django.conf import settings
from oauth2_provider.views.generic import ReadWriteScopedResourceView


class PersonView(RESTDispatch, ReadWriteScopedResourceView):
    """Information (username, email) about a person"""

    def get(self, request):
        user = self._get_user(request)

        data = {
            "user": user.username,
            "email": "",
        }

        if hasattr(settings, "USER_EMAIL_DOMAIN"):
            data["email"] = user.username + "@" + settings.USER_EMAIL_DOMAIN

        return JSONResponse(data)
