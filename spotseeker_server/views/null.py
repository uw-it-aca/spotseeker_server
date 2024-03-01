# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" This class is just here to help with testing coverage
"""
from spotseeker_server.views.rest_dispatch import RESTDispatch


class NullView(RESTDispatch):
    pass
