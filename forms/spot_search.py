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

from spotseeker_server.default_forms.spot_search import DefaultSpotSearchForm
from django.utils.importlib import import_module
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class SpotSearchForm(object):
    def __new__(*args, **named_args):

        if hasattr(settings, 'SPOTSEEKER_SPOT_SEARCH_FORM'):
            # This is all taken from django's static file finder
            module, attr = settings.SPOTSEEKER_SPOT_SEARCH_FORM.rsplit('.', 1)
            try:
                mod = import_module(module)
            except ImportError, e:
                raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                           (module, e))
            try:
                FormModule = getattr(mod, attr)
            except AttributeError:
                raise ImproperlyConfigured('Module "%s" does not define a "%s" '
                                           'class.' % (module, attr))

            return FormModule(args[1])
        else:
            return DefaultSpotSearchForm(args[1])
