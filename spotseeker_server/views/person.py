# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from spotseeker_server.views.rest_dispatch import RESTDispatch, JSONResponse
from spotseeker_server.require_auth import user_auth_required
from django.conf import settings


class PersonView(RESTDispatch):
    """Information (username, email) about a person"""

    # @user_auth_required
    def GET(self, request):
        user = self._get_user(request)

        data = {
            "user": user.username,
            "email": "",
        }

        if hasattr(settings, "USER_EMAIL_DOMAIN"):
            data["email"] = user.username + "@" + settings.USER_EMAIL_DOMAIN

        return JSONResponse(data)
