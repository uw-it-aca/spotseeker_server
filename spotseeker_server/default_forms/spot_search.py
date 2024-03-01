# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django import forms


class DefaultSpotSearchForm(forms.Form):
    distance = forms.FloatField(required=False)
    center_latitude = forms.FloatField(
        required=False, max_value=90, min_value=-90
    )
    center_longitude = forms.FloatField(
        required=False, max_value=180, min_value=-180
    )
