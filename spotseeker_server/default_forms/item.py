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

from django import forms
from spotseeker_server.models import Item, ItemExtendedInfo
import re


class DefaultItemExtendedInfoForm(forms.ModelForm):

    class Meta:
        model = ItemExtendedInfo

    def clean_key(self):
        key = self.cleaned_data['key'].strip()
        if not re.match(r'^[a-z0-9_-]+$', key, re.I):
            raise forms.ValidationError(
                "Key must be only alphanumerics, underscores, and hyphens")
        return key


class DefaultItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ('name',)
