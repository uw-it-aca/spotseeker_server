""" Copyright 2013, 2014 UW Information Technology, University of Washington

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

    bypasses_auth = False
    trusted_client = TrustedOAuthClient.objects.filter(consumer = consumer)
    if len(trusted_client) and trusted_client[0].bypasses_user_authorization:
        bypasses_auth = True

    request.session['oauth'] = token.key
    return render_to_response("oauth/authorize.html", {
        "consumer": consumer.name,
        "token": request.GET["oauth_token"],
        "bypass_auth": bypasses_auth,
    }, RequestContext(request))


def callback(request, **kwargs):
    if "oauth_token" not in kwargs:
        return render_to_response("oauth/declined.html")

    token = Token.objects.get(key = kwargs["oauth_token"])

    return render_to_response("oauth/oob.html", {
        "verifier": token.verifier,
    }, RequestContext(request))

