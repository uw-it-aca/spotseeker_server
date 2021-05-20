# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

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

    sbutler1@illinois.edu: only load the auth modules once on app
        initialization.
    ^ This is being reverted back to being loaded every time. After
    profiling, it didn't seem like there was hardly any speed
    difference, and only loading this once on application load
    breaks our unit tests.
"""

from django.http import HttpResponse
from django.core.exceptions import ImproperlyConfigured
import spotseeker_server.auth.all_ok
from spotseeker_server.load_module import load_module_by_name

from functools import wraps

from django.conf import settings


def get_auth_module():
    try:
        mod_name = settings.SPOTSEEKER_AUTH_MODULE
    except NameError:
        return spotseeker_server.auth.all_ok
    return load_module_by_name(mod_name)


def get_auth_method(method_name):
    mod = get_auth_module()
    try:
        return getattr(mod, method_name)
    except (AttributeError, NameError):
        raise ImproperlyConfigured('Module "%s" does not define a "%s" '
                                   'method.' % (module, method_name))


def check_auth(method_name, func, *args, **kwargs):
    method = get_auth_method(method_name)
    bad_response = method(*args, **kwargs)
    if bad_response:
        return bad_response
    else:
        return func(*args, **kwargs)


def app_auth_required(func):
    @wraps(func)
    def _checkAuth(*args, **kwargs):
        return check_auth('authenticate_application', func, *args, **kwargs)
    return _checkAuth


def user_auth_required(func):
    @wraps(func)
    def _checkAuth(*args, **kwargs):
        return check_auth('authenticate_user', func, *args, **kwargs)
    return _checkAuth


def admin_auth_required(func):

    @wraps(func)
    def _checkAuth(*args, **kwargs):
        ###
        # XXX - this needs to change to something else.  stop-gap measure
        ###
        bad_response = HttpResponse("Error - admin access required")
        bad_response.status_code = 401

        if not hasattr(settings, "SPOTSEEKER_AUTH_ADMINS"):
            print("Set SPOTSEEKER_AUTH_ADMINS in your settings.py")
            return bad_response

        admins = settings.SPOTSEEKER_AUTH_ADMINS
        if not isinstance(admins, (list, tuple)):
            print("SPOTSEEKER_AUTH_ADMINS must be a list or tuple")
            return bad_response

        request = args[1]
        username = request.META['SS_OAUTH_USER']
        if username not in admins:
            return bad_response

        return func(*args, **kwargs)
    return _checkAuth
