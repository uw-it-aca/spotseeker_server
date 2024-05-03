# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from spotseeker_server.default_forms.item import (
    DefaultItemForm,
    DefaultItemExtendedInfoForm,
)
from spotseeker_server.load_module import ModuleObjectLoader


class ItemExtendedInfoForm(ModuleObjectLoader):
    setting_name = "SPOTSEEKER_ITEMEXTENDEDINFO_FORM"
    default = DefaultItemExtendedInfoForm


class ItemForm(ModuleObjectLoader):
    setting_name = "SPOTSEEKER_ITEM_FORM"
    default = DefaultItemForm
