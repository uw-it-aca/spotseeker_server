# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from oauth_provider.models import Token
from spotseeker_server.models import TrustedOAuthClient


def authorize(request, token, callback, params):
    consumer = token.consumer

    bypasses_auth = False
    trusted_client = TrustedOAuthClient.objects.filter(consumer=consumer)
    if len(trusted_client) and trusted_client[0].bypasses_user_authorization:
        bypasses_auth = True

    request.session["oauth"] = token.key
    return render_to_response(
        "oauth/authorize.html",
        {
            "consumer": consumer.name,
            "token": request.GET["oauth_token"],
            "bypass_auth": bypasses_auth,
        },
        RequestContext(request),
    )


def callback(request, **kwargs):
    if "oauth_token" not in kwargs:
        return render_to_response("oauth/declined.html")

    token = Token.objects.get(key=kwargs["oauth_token"])

    return render_to_response(
        "oauth/oob.html",
        {
            "verifier": token.verifier,
        },
        RequestContext(request),
    )
