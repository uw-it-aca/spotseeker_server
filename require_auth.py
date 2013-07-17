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
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
import spotseeker_server.auth.all_ok

from functools import wraps

from django.conf import settings


def app_auth_required(func):

    def _checkAuth(*args, **kwargs):
        if hasattr(settings, 'SPOTSEEKER_AUTH_MODULE'):
            module = settings.SPOTSEEKER_AUTH_MODULE
            try:
                mod = import_module(module)
            except ImportError, e:
                raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                           (module, e))

            try:
                method = getattr(mod, "authenticate_application")
            except AttributeError:
                raise ImproperlyConfigured('Module "%s" does not define a "authenticate_application" method.' % module)

            bad_response = method(*args, **kwargs)
        else:
            bad_response = spotseeker_server.auth.all_ok.authenticate_application(*args, **kwargs)

        if bad_response:
            return bad_response
        else:
            return func(*args, **kwargs)
    return wraps(func)(_checkAuth)


def user_auth_required(func):

    def _checkAuth(*args, **kwargs):
        if hasattr(settings, 'SPOTSEEKER_AUTH_MODULE'):
            module = settings.SPOTSEEKER_AUTH_MODULE
            try:
                mod = import_module(module)
            except ImportError, e:
                raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                           (module, e))

            try:
                method = getattr(mod, "authenticate_user")
            except AttributeError:
                raise ImproperlyConfigured('Module "%s" does not define a "authenticate_user" method.' % module)

            bad_response = method(*args, **kwargs)
        else:
            bad_response = spotseeker_server.auth.all_ok.authenticate_user(*args, **kwargs)

        if bad_response:
            return bad_response
        else:
            return func(*args, **kwargs)
    return wraps(func)(_checkAuth)
