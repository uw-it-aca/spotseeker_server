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

    sbutler1@illinois.edu: load the forms on application load, not every
        request for a form.
    ^ This is being reverted back to being loaded every time SpotForm is
    called. After profiling, it didn't seem like there was hardly any
    speed difference, and only loading this once on application load
    breaks our unit tests.
"""

from spotseeker_server.default_forms.spot import \
    DefaultSpotForm, DefaultSpotExtendedInfoForm
from spotseeker_server.load_module import ModuleObjectLoader


class SpotExtendedInfoForm(ModuleObjectLoader):
    setting_name = 'SPOTSEEKER_SPOTEXTENDEDINFO_FORM'
    default = DefaultSpotExtendedInfoForm


class SpotForm(ModuleObjectLoader):
    setting_name = 'SPOTSEEKER_SPOT_FORM'
    default = DefaultSpotForm
