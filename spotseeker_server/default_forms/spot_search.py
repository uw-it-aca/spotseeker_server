# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

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


class DefaultSpotSearchForm(forms.Form):
    distance = forms.FloatField(required=False)
    center_latitude = forms.FloatField(required=False,
                                       max_value=90,
                                       min_value=-90)
    center_longitude = forms.FloatField(required=False,
                                        max_value=180,
                                        min_value=-180)
