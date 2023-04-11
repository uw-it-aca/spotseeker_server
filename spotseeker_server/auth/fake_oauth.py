# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" This module will allow all requests, without requiring authentication or
authorization.  To use it, add this to your settings.py:

SPOTSEEKER_AUTH_MODULE = spotseeker_server.auth.fake_oauth

You can specify a user with a request header of ??? (Missing at time of commit)
"""

from django.contrib import auth


def authenticate_application(*args, **kwargs):
    """This always allows requests through"""
    return


def authenticate_user(*args, **kwargs):
    """This always allows requests through"""
    request = args[1]

    input_username = request.META["TESTING_OAUTH_USER"]
    user = auth.authenticate(remote_user=input_username)
    request.META["SS_OAUTH_USER"] = user.username
    return
