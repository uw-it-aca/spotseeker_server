""" Copyright 2014 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""

from spotseeker_server.views.rest_dispatch import RESTDispatch, JSONResponse
from spotseeker_server.require_auth import user_auth_required
from django.views.decorators.cache import never_cache
from django.conf import settings

class PersonView(RESTDispatch):
    """ Information (username, email) about a person """
    @user_auth_required
    @never_cache
    def GET(self, request):
        user = self._get_user(request)

        data = {
            "user": user.username,
            "email": "",
        }

        if hasattr(settings, "USER_EMAIL_DOMAIN"):
            data["email"] = user.username + "@" + settings.USER_EMAIL_DOMAIN

        return JSONResponse(data)

