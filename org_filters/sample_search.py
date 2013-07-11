""" Copyright 2013 Board of Trustees, University of Illinois

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Description
    =================================================================
    A sample search filter.
"""
import logging
import re
from spotseeker_server.models import SpotExtendedInfo
from spotseeker_server.org_filters import SearchFilter

# UIUC LDAP
LOGGER = logging.getLogger(__name__)

class Filter(SearchFilter):
    keys = set((
        'sample1',
        'extended_info:sample2',
        ))

    def filter_query(self, query):
        """
        When searching on sample2, extend it in the following way:

        - foo: includes bar and baz
        - bar: includes baz
        """

        if 'extended_info:sample2' in self.request.GET:
            sample = self.request.GET["extended_info:sample2"]
            if sample:
                values = [sample]
                if sample == 'foo':
                    values.append('bar')
                    values.append('baz')
                elif sample == 'bar':
                    values.append('baz')
                query = query.filter(
                        spotextendedinfo__key="sample2",
                        spotextendedinfo__value__in=values
                        )

                self.has_valid_search_param = True

        return query

    def filter_results(self, spots):
        """
        Only include a spot if the query specified 'sample1'
        and the ID is even.
        """

        sample = self.request.GET.get('sample1', '')
        if not sample:
            result = spots
        else:
            result = set()
            for spot in spots: 
                if spot.id % 2 == 0:
                    result.add(spot)

        return result

