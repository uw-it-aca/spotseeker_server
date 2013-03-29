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


# dict of all of the uiuc extended info with values that must be validated
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
    "food_allowed": ['none', 'any', 'covered_drink'],
    "num_computers": "int",
    "reservable": ['true', 'reservations'],
    "noise_level": ['silent', 'quiet', 'moderate', 'loud', 'variable'],
    "uiuc_require_address": "re",
}


def uiuc_validate(value, choices):
    """ Check to see if the value is one of the choices or if it is an int, else it throws a validation error
    """
    if choices == "int":
        try:
            int(value)
        except:
            raise forms.ValidationError("Value must be an int")
    if choices == "re":
        try:
            re.compile(value)
        except:
            raise forms.ValidationError("Value must be a regular expression")
    elif not value in choices:
        raise forms.ValidationError("Value must be one of %s" % choices)


def validate_uiuc_extended_info(value):
    # TODO: access_restrictions require access_notes to be there, reservable requires reservation_notes
    # UW Spots must have extended_info
    if value is None:
        raise forms.ValidationError("You must have an extended_info section")

    # orientation, location_description, access_notes, reserve_notes, hours_notes, may be any string
    for key in validated_ei:
        if key in value:
            uiuc_validate(value[key], validated_ei[key])
    return True


class ExtendedInfoField(forms.Field):
    def to_python(self, value):
        if value is not None:
            for k in value.keys():
                if value[k] == '':
                    del value[k]
        return value

    def validate(self, value):
        return validate_uiuc_extended_info(value)


class ExtendedInfoForm(forms.ModelForm):
    class Meta:
        model = SpotExtendedInfo

    def clean_value(self):
        if validate_uiuc_extended_info({self.data['key']: self.data['value']}):
            return self.data['value']


class UWSpotForm(forms.Form):
    class Meta:
        model = Spot
        fields = ('name', 'capacity')

    validated_extended_info = validated_ei
    extended_info = ExtendedInfoField()
