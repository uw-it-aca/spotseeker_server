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
from spotseeker_server.models import Spot, SpotExtendedInfo
import simplejson as json
import re


# dict of all of the uw extended info with values that must be validated
# and what all of the possible validated values are, or validated types
validated_ei = {
    "has_whiteboards": ['true'],
    "has_outlets": ['true'],
    "has_printing": ['true'],
    "has_scanner": ['true'],
    "has_displays": ['true'],
    "has_projector": ['true'],
    "has_computers": ['true'],
    "has_natural_light": ['true'],
    "food_nearby": ['space', 'building', 'neighboring'],
    "num_computers": "int",
    "reservable": ['true', 'reservations'],
    "noise_level": ['silent', 'quiet', 'moderate', 'loud', 'variable'],
}


def uw_validate(value, choices):
    """ Check to see if the value is one of the choices or if it is an int, else it throws a validation error
    """
    if choices == "int":
        try:
            int(value)
        except:
            raise forms.ValidationError("Value must be an int")
    elif not value in choices:
        raise forms.ValidationError("Value must be one of: {0}".format('; '.join(choices)))


class ExtendedInfoForm(forms.ModelForm):
    class Meta:
        model = SpotExtendedInfo

    def clean_key(self):
        key = self.cleaned_data['key']
        if not re.match(r'^[a-z0-9_-]+$', key, re.I):
            raise forms.ValidationError("Key must be only alphanumerics, underscores, and hyphens")
        return key

    def clean_value(self):
        key = self.cleaned_data['key']
        value = self.cleaned_data['value']

        if key in validated_ei:
            uw_validate(value, validated_ei[key])

        return value



class UWSpotForm(forms.ModelForm):
    class Meta:
        model = Spot

    validated_extended_info = validated_ei

    def clean_external_id(self):
        return self.cleaned_data['external_id'] or None
