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

    sbutler1@illinois.edu: add import for ImproperlyConfigured.
"""

from spotseeker_server.default_forms.spot_search import DefaultSpotSearchForm
from spotseeker_server.load_module import ModuleObjectLoader


class SpotSearchForm(ModuleObjectLoader):
    setting_name = 'SPOTSEEKER_SPOT_SEARCH_FORM'
    default = DefaultSpotSearchForm
