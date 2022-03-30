# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" Changes
    =================================================================

    sbutler1@illinois.edu: adapted to the new form framework.
"""

from django import forms
from django.dispatch import receiver
from spotseeker_server.default_forms.spot import DefaultSpotForm
from spotseeker_server.default_forms.spot import DefaultSpotExtendedInfoForm
from spotseeker_server.models import Spot, SpotExtendedInfo
from spotseeker_server.dispatch import spot_post_build
import simplejson as json
import re
import phonenumbers


# dict of all of the uw extended info with values that must be validated
# and what all of the possible validated values are, or validated types
validated_ei = {
    "app_type": ["food", "tech"],
    "auto_labstats_available": "int",
    "auto_labstats_total": "int",
    "campus": ["seattle", "tacoma", "bothell", "south_lake_union"],
    "food_nearby": ["space", "building", "neighboring"],
    "has_computers": ["true"],
    "has_displays": ["true"],
    "has_labstats": ["true"],
    "has_natural_light": ["true"],
    "has_outlets": ["true"],
    "has_printing": ["true"],
    "has_projector": ["true"],
    "has_scanner": ["true"],
    "has_whiteboards": ["true"],
    "is_hidden": ["true"],
    "labstats_id": "int",
    "location_description": "str",
    "noise_level": ["silent", "quiet", "moderate", "variable"],
    "num_computers": "int",
    "rating": "int",
    "reservable": ["true", "reservations"],
    "review_count": "int",
    "s_cuisine_american": ["true"],
    "s_cuisine_bbq": ["true"],
    "s_cuisine_chinese": ["true"],
    "s_cuisine_hawaiian": ["true"],
    "s_cuisine_indian": ["true"],
    "s_cuisine_italian": ["true"],
    "s_cuisine_korean": ["true"],
    "s_cuisine_mexican": ["true"],
    "s_cuisine_vietnamese": ["true"],
    "s_food_breakfast": ["true"],
    "s_food_burgers": ["true"],
    "s_food_curry": ["true"],
    "s_food_desserts": ["true"],
    "s_food_entrees": ["true"],
    "s_food_espresso": ["true"],
    "s_food_frozen_yogurt": ["true"],
    "s_food_groceries": ["true"],
    "s_food_pasta": ["true"],
    "s_food_pastries": ["true"],
    "s_food_pho": ["true"],
    "s_food_pizza": ["true"],
    "s_food_salads": ["true"],
    "s_food_sandwiches": ["true"],
    "s_food_smoothies": ["true"],
    "s_food_sushi_packaged": ["true"],
    "s_food_tacos": ["true"],
    "s_has_reservation": ["true"],
    "s_pay_cash": ["true"],
    "s_pay_dining": ["true"],
    "s_pay_husky": ["true"],
    "s_pay_mastercard": ["true"],
    "s_pay_visa": ["true"],
}


def uw_validate(value, key, choices):
    """Check to see if the value is one of the choices or if it is an
    int or str, else it throws a validation error
    """
    if choices == "int":
        try:
            int(value)
        except ValueError:
            raise forms.ValidationError("Value must be an int")
    elif choices == "str":
        if value.isdecimal():
            raise forms.ValidationError(
                "Location description cannot contain only numbers"
            )
    elif value not in choices:
        raise forms.ValidationError(
            "Value for %s was %s, must be one of: %s"
            % (key, repr(value), "; ".join((repr(c) for c in choices)))
        )


class UWSpotExtendedInfoForm(DefaultSpotExtendedInfoForm):
    def clean(self):
        cleaned_data = super(UWSpotExtendedInfoForm, self).clean()
        # Have to check value here since we look at multiple items
        key = self.cleaned_data["key"]

        # if location description all whitespace, django cleans value to None
        if key == "location_description":
            try:
                value = self.cleaned_data["value"]
            except KeyError as e:
                value = self.cleaned_data.get("value")
                if value is None:
                    raise forms.ValidationError(
                        "Location description cannot contain only spaces"
                    )

        value = self.cleaned_data["value"]

        if key == "s_phone":
            p = re.compile("[A-Za-z]")
            if p.search(value):
                raise forms.ValidationError(
                    "Phone number cannot contain " "letters"
                )

            try:
                number = phonenumbers.parse(value, "US")

                if not phonenumbers.is_valid_number(
                    number
                ) or not phonenumbers.is_possible_number(number):
                    raise forms.ValidationError("")

                value = phonenumbers.format_number(
                    number, phonenumbers.PhoneNumberFormat.E164
                )
                cleaned_data["value"] = value[2:]
            except Exception as ex:
                raise forms.ValidationError("s_phone must be a phone number")

        elif key in validated_ei:
            uw_validate(value, key, validated_ei[key])

        return cleaned_data


class UWSpotForm(DefaultSpotForm):
    validated_extended_info = validated_ei


@receiver(spot_post_build, sender=UWSpotForm)
def uw_validate_has_extended_info(sender, **kwargs):
    """
    After a spot REST request has been processed, validate that it contained
    some extended info.
    """
    spot = kwargs["spot"]
    if spot.spotextendedinfo_set.count() <= 0:
        raise forms.ValidationError("UWSpot must have extended info")
