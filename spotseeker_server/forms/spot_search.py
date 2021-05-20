# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" Changes
    =================================================================

    sbutler1@illinois.edu: add import for ImproperlyConfigured.
"""

from spotseeker_server.default_forms.spot_search import DefaultSpotSearchForm
from spotseeker_server.load_module import ModuleObjectLoader


class SpotSearchForm(ModuleObjectLoader):
    setting_name = "SPOTSEEKER_SPOT_SEARCH_FORM"
    default = DefaultSpotSearchForm
