# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" This module will allow all requests, without requiring authentication or
authorization.  To use it, add this to your settings.py:

SPOTSEEKER_AUTH_MODULE = spotseeker_server.auth.all_ok

By default authenticate_user will use the user demo_user.  You can override
this in settings.py:

SPOTSEEKER_AUTH_ALL_USER = 'other_user'
"""
from django.conf import settings
from django.contrib.auth.models import User


def authenticate_application(*args, **kwargs):
    """This always allows requests through"""
    return


def authenticate_user(*args, **kwargs):
    """This always allows requests through"""
    request = args[1]
    username = getattr(settings, "SPOTSEEKER_AUTH_ALL_USER", "demo_user")

    user_obj = User.objects.get_or_create(username=username)
    request.META["SS_OAUTH_USER"] = username
    return
