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
"""

from django.http import HttpResponse
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
import spotseeker_server.auth.all_ok

from functools import wraps

from django.conf import settings

if hasattr(settings, 'SPOTSEEKER_AUTH_MODULE'):
    module = settings.SPOTSEEKER_AUTH_MODULE
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                   (module, e))

    try:
        APP_AUTH_METHOD = getattr(mod, "authenticate_application")
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "authenticate_application" method.' % module)

    try:
        USER_AUTH_METHOD = getattr(mod, "authenticate_user")
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "authenticate_user" method.' % module)
else:
    APP_AUTH_METHOD = spotseeker_server.auth.all_ok.authenticate_application
    USER_AUTH_METHOD = spotseeker_server.auth.all_ok.authenticate_user

def app_auth_required(func):

    def _checkAuth(*args, **kwargs):
        bad_response = APP_AUTH_METHOD(*args, **kwargs)
        if bad_response:
            return bad_response
        else:
            return func(*args, **kwargs)
    return wraps(func)(_checkAuth)


def user_auth_required(func):

    def _checkAuth(*args, **kwargs):
        bad_response = USER_AUTH_METHOD(*args, **kwargs)
        if bad_response:
            return bad_response
        else:
            return func(*args, **kwargs)
    return wraps(func)(_checkAuth)
