# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" Changes
    =================================================================

    sbutler1@illinois.edu: load the forms on application load, not every
        request for a form.
    ^ This is being reverted back to being loaded every time SpotForm is
    called. After profiling, it didn't seem like there was hardly any
    speed difference, and only loading this once on application load
    breaks our unit tests.
"""

from spotseeker_server.default_forms.spot import (
    DefaultSpotForm,
    DefaultSpotExtendedInfoForm,
)
from spotseeker_server.load_module import ModuleObjectLoader


class SpotExtendedInfoForm(ModuleObjectLoader):
    setting_name = "SPOTSEEKER_SPOTEXTENDEDINFO_FORM"
    default = DefaultSpotExtendedInfoForm


class SpotForm(ModuleObjectLoader):
    setting_name = "SPOTSEEKER_SPOT_FORM"
    default = DefaultSpotForm
