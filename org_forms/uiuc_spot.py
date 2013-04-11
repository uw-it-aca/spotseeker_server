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

    sbutler1@illinois.edu: copied from org_forms/uw_spot.py and
        adapted for the UIUC spot schema.
"""

from django import forms
from django.dispatch import receiver
from spotseeker_server.models import Spot, SpotExtendedInfo
from spotseeker_server.default_forms.spot import DefaultSpotForm, DefaultSpotExtendedInfoForm
from spotseeker_server.dispatch import spot_post_build
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
        raise forms.ValidationError("Value must be one of: {0}".format('; '.join(choices)))


class UIUCSpotExtendedInfoForm(DefaultSpotExtendedInfoForm):
    def clean(self):
        cleaned_data = super(UIUCSpotExtendedInfoForm, self).clean()

        # Have to check value here since we look at multiple items
        key = self.cleaned_data['key']
        value = self.cleaned_data['value']

        if key in validated_ei:
            uiuc_validate(value, validated_ei[key])

        return cleaned_data


class UIUCSpotForm(DefaultSpotForm):
    validated_extended_info = validated_ei


@receiver(spot_post_build, sender=UIUCSpotForm)
def uiuc_validate_has_extended_info(sender, **kwargs):
    """
    After a spot REST request has been processed, validate that it contained
    some extended info.
    """
    spot = kwargs['spot']
    if SpotExtendedInfo.objects.filter(spot=spot).count() <= 0:
        raise forms.ValidationError("UIUCSpot must have extended info")
