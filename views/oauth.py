""" Copyright 2013 UW Information Technology, University of Washington

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

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from oauth_provider.models import Token
from spotseeker_server.models import TrustedOAuthClient

def authorize(request, token, callback, params):
    consumer = token.consumer

    # XXX - create a level between trusted and untrusted, that is allowed
    # to skip authorization, but still must use 3-legged oauth to identify
    # users.

    request.session['oauth'] = token.key
    return render_to_response("oauth/authorize.html", {
        "consumer": consumer.name,
        "token": request.GET["oauth_token"],
    }, RequestContext(request))


def callback(request, **kwargs):
    token = Token.objects.get(key = kwargs["oauth_token"])

    return render_to_response("oauth/oob.html", {
        "verifier": token.verifier,
    }, RequestContext(request))

