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

    sbutler1@illinois.edu: moved from views/spot.py and adapted for
        the search filter framework.
"""
from spotseeker_server.org_filters import SearchFilter

class Filter(SearchFilter):
    keys = set((
        'extended_info:reservable',
        'extended_info:noise_level',
        ))

    def filter_query(self, query):
        """Filter based on reservable and noise_level."""

        if 'extended_info:reservable' in self.request.GET:
            query = query.filter(
                    spotextendedinfo__key="reservable",
                    spotextendedinfo__value__in=['true', 'reservations']
                    )

        if 'extended_info:noise_level' in self.request.GET:
            noise_levels = self.request.GET.getlist("extended_info:noise_level")

            exclude_silent = True
            exclude_quiet = True
            exclude_moderate = True
            exclude_variable = True

            for level in noise_levels:
                if "silent" == level:
                    exclude_silent = False
                if "quiet" == level:
                    exclude_quiet = False
                    exclude_variable = False
                if "moderate" == level:
                    exclude_moderate = False
                    exclude_variable = False

            if exclude_silent:
                query = query.exclude(
                        spotextendedinfo__key="noise_level",
                        spotextendedinfo__value__iexact="silent"
                        )

            if exclude_quiet:
                query = query.exclude(
                        spotextendedinfo__key="noise_level",
                        spotextendedinfo__value__iexact="quiet"
                        )

            if exclude_moderate:
                query = query.exclude(
                        spotextendedinfo__key="noise_level",
                        spotextendedinfo__value__iexact="moderate"
                        )

            if exclude_variable:
                query = query.exclude(
                        spotextendedinfo__key="noise_level",
                        spotextendedinfo__value__iexact="variable"
                        )

        return query
