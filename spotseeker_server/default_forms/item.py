# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django import forms
from spotseeker_server.models import Item, ItemExtendedInfo
import re


class DefaultItemExtendedInfoForm(forms.ModelForm):
    class Meta:
        model = ItemExtendedInfo
        fields = "__all__"

    def clean_key(self):
        key = self.cleaned_data["key"].strip()
        if not re.match(r"^[a-z0-9_-]+$", key, re.I):
            raise forms.ValidationError(
                "Key must be only alphanumerics, underscores, and hyphens"
            )
        return key


class DefaultItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ("name", "item_category", "item_subcategory")
