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

    sbutler1@illinois.edu: added data validation; made the forms
        useful for the admin interface.
"""

from decimal import Decimal
from django import forms
from spotseeker_server.models import Spot, SpotExtendedInfo
import re

LATITUDE_MAX    = Decimal('90')
LATITUDE_MIN    = Decimal('-90')
LONGITUDE_MAX   = Decimal('180')
LONGITUDE_MIN   = Decimal('-180')

class DefaultSpotExtendedInfoForm(forms.ModelForm):
    class Meta:
        model = SpotExtendedInfo

    def clean_key(self):
        key = self.cleaned_data['key'].strip()
        if not re.match(r'^[a-z0-9_-]+$', key, re.I):
            raise forms.ValidationError("Key must be only alphanumerics, underscores, and hyphens")
        return key

class DefaultSpotForm(forms.ModelForm):
    class Meta:
        model = Spot
        exclude = ('etag', 'last_modified')

    validated_extended_info = {}

    def clean_building_name(self):
        return self.cleaned_data['building_name'].strip()

    def clean_capacity(self):
        capacity = self.cleaned_data['capacity']
        if capacity is None:
            pass
        elif capacity < 0:
            raise forms.ValidationError("Capacity must be non-negative")
        elif capacity == 0:
            capacity = None
        return capacity

    def clean_external_id(self):
        return self.cleaned_data['external_id'] or None

    def clean_floor(self):
        return self.cleaned_data['floor'].strip()

    def clean_latitude(self):
        latitude = self.cleaned_data['latitude']
        if latitude is None:
            raise forms.ValidationError("Latitude is required")
        if latitude < LATITUDE_MIN:
            raise forms.ValidationError("Latitude is too small")
        elif latitude > LATITUDE_MAX:
            raise forms.ValidationError("Latitude is too large")
        return latitude

    def clean_longitude(self):
        longitude = self.cleaned_data['longitude']
        if longitude is None:
            raise forms.ValidationError("Longitude is required")
        if longitude < LONGITUDE_MIN:
            raise forms.ValidationError("Longitude is too small")
        elif longitude > LONGITUDE_MAX:
            raise forms.ValidationError("Longitude is too large")
        return longitude

    def clean_manager(self):
        return self.cleaned_data['manager'].strip()

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if not name:
            raise forms.ValidationError("Invalid name")
        return name

    def clean_organization(self):
        return self.cleaned_data['organization'].strip()

    def clean_room_number(self):
        return self.cleaned_data['room_number'].strip()
