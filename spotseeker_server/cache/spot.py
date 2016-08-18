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

"""
from django.utils.importlib import import_module
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import default_cache


class SpotCache(object):
    @staticmethod
    def implementation():
        if hasattr(settings, 'SPOTSEEKER_SPOT_CACHE'):
            # This is all taken from django's static file finder
            module = settings.SPOTSEEKER_SPOT_CACHE
            try:
                cache = import_module(module)
            except ImportError, e:
                raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                           (module, e))
            return cache
        else:
            return default_cache

    def __new__(cls):
        return cls.implementation()
