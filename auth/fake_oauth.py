""" Copyright 2014 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.


This module will allow all requests, without requiring authentication or
authorization.  To use it, add this to your settings.py:

SPOTSEEKER_AUTH_MODULE = spotseeker_server.auth.fake_oauth

You can specify a user with a request header of 

"""

from django.contrib import auth

def authenticate_application(*args, **kwargs):
    """ This always allows requests through """
    return


def authenticate_user(*args, **kwargs):
    """ This always allows requests through """
    request = args[1]

    input_username = request.META['TESTING_OAUTH_USER']
    user = auth.authenticate(remote_user=input_username)
    request.META['SS_OAUTH_USER'] = user.username
    return
