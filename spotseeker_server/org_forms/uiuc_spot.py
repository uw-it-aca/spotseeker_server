# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" Changes
    =================================================================

    sbutler1@illinois.edu: copied from org_forms/uw_spot.py and
        adapted for the UIUC spot schema.
"""

from django import forms
from django.dispatch import receiver
from spotseeker_server.models import Spot, SpotExtendedInfo
from spotseeker_server.default_forms.spot import DefaultSpotForm
from spotseeker_server.default_forms.spot import DefaultSpotExtendedInfoForm
from spotseeker_server.dispatch import spot_post_build
import simplejson as json
import re


# dict of all of the uiuc extended info with values that must be validated
# and what all of the possible validated values are, or validated types
validated_ei = {
    "has_whiteboards": ["true"],
    "has_outlets": ["true"],
    "has_printing": ["true"],
    "has_scanner": ["true"],
    "has_displays": ["true"],
    "has_projector": ["true"],
    "has_computers": ["true"],
    "has_natural_light": ["true"],
    "food_nearby": ["space", "building", "neighboring"],
    "food_allowed": ["none", "any", "covered_drink"],
    "num_computers": "int",
    "reservable": ["true", "reservations"],
    "noise_level": ["silent", "quiet", "moderate", "loud", "variable"],
    "uiuc_require_address": "re",
}


def uiuc_validate(value, choices):
    """Check to see if the value is one of the choices or if it is an int,
    else it throws a validation error
    """
    if choices == "int":
        try:
            int(value)
        except ValueError:
            raise forms.ValidationError("Value must be an int")
    if choices == "re":
        try:
            re.compile(value)
        except TypeError:
            raise forms.ValidationError("Value must be a regular expression")
    elif value not in choices:
        raise forms.ValidationError(
            "Value must be one of: {0}".format("; ".join(choices))
        )


class UIUCSpotExtendedInfoForm(DefaultSpotExtendedInfoForm):
    def clean(self):
        cleaned_data = super(UIUCSpotExtendedInfoForm, self).clean()

        # Have to check value here since we look at multiple items
        key = self.cleaned_data["key"]
        value = self.cleaned_data["value"]

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
    spot = kwargs["spot"]
    if SpotExtendedInfo.objects.filter(spot=spot).count() <= 0:
        raise forms.ValidationError("UIUCSpot must have extended info")
