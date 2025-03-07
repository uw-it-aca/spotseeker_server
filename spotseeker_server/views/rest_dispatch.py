# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" Changes
    =================================================================

    sbutler1@illinois.edu: add JSONResponse subclass of HttpResponse;
        add some exceptions for subclass views to raise; simplify
        choosing a method to call; catch exceptions and return them
        to the client (always with an error field); move etag
        validation to here.
"""

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.conf import settings
from django.http import HttpResponse
from oauth2_provider.models import get_access_token_model
import simplejson as json
import traceback
import logging


logger = logging.getLogger(__name__)

AccessToken = get_access_token_model()


class JSONResponse(HttpResponse):
    """
    A standard HttpResponse that will serialize the body to JSON
    and set the content-type to 'application/json'
    """

    def __init__(self, content="", *args, **kwargs):
        debug = getattr(settings, "DEBUG", False)
        pretty_print = getattr(settings, "JSON_PRETTY_PRINT", False)
        if content != "":
            if debug and pretty_print:
                content = json.dumps(content, sort_keys=True, indent=4 * " ")
            else:
                content = json.dumps(content)

        if not kwargs.get("content_type", None):
            kwargs["content_type"] = "application/json"

        super(JSONResponse, self).__init__(content, *args, **kwargs)


class RESTException(Exception):
    """
    Can be thrown inside RESTful methods. Accepts a specific
    status code to use, or 500 by default.
    """

    def __init__(self, message, status_code):
        super(RESTException, self).__init__(message)
        self.status_code = status_code


class RESTFormInvalidError(RESTException):
    """Thrown when a form is invalid, and holds all the errors."""

    def __init__(self, form):
        super(RESTFormInvalidError, self).__init__("Form is invalid", 400)
        self.form = form


class RESTDispatch:
    """Handles passing on the request to the correct view
    method based on the request type.
    """

    def run(self, *args, **named_args):
        request = args[0]
        method = request.META["REQUEST_METHOD"]

        try:
            if settings.SPOTSEEKER_OAUTH_ENABLED:
                self.validate_oauth_scope(request, method)

            if "GET" == method and hasattr(self, "get"):
                response = self.get(*args, **named_args)
            elif "POST" == method and hasattr(self, "post"):
                response = self.post(*args, **named_args)
            elif "PUT" == method and hasattr(self, "put"):
                response = self.put(*args, **named_args)
            elif "DELETE" == method and hasattr(self, "delete"):
                response = self.delete(*args, **named_args)
            else:
                raise RESTException("Method not allowed", 405)

        except ObjectDoesNotExist as odne:
            json_values = self.json_error(odne)
            response = JSONResponse(json_values, status=404)

        except ValidationError as ve:
            json_values = self.json_error(ve)
            response = JSONResponse(json_values, status=400)

        except RESTFormInvalidError as fie:
            json_values = self.json_error(fie)
            json_values.update(fie.form.errors)
            response = JSONResponse(json_values, status=fie.status_code)

        except RESTException as rest_e:
            json_values = self.json_error(rest_e)
            response = JSONResponse(json_values, status=rest_e.status_code)

        except Exception as e:
            json_values = self.json_error(e)
            response = JSONResponse(json_values, status=500)

        return response

    def json_error(self, ex):
        json_values = {"error": str(ex)}

        if getattr(settings, "DEBUG", False):
            json_values["stack"] = traceback.format_exc().splitlines()

        return json_values

    def validate_etag(self, request, obj):
        if "HTTP_IF_MATCH" not in request.META:
            if "If_Match" not in request.META:
                raise RESTException("If-Match header required", 400)
            else:
                request.META["HTTP_IF_MATCH"] = request.META["If_Match"]

        if request.META["HTTP_IF_MATCH"] != obj.etag:
            raise RESTException("Invalid ETag", 409)

    def validate_oauth_scope(self, request, method: str) -> None:
        if "Authorization" not in request.headers:
            raise RESTException("Missing Authorization header", 401)

        access_token = request.headers.get("Authorization").split(" ")[1]

        try:
            token = AccessToken.objects.get(token=access_token)

            if token.is_expired():
                raise RESTException("Expired access token", 401)

        except AccessToken.DoesNotExist:
            raise RESTException("Invalid access token", 401)

        scope = token.scope
        logger.debug(f"Validating scope: {scope}")

        # match scope with request method
        if method == "GET":
            if "read" not in scope:
                raise RESTException(f"Invalid scope for method {method}", 403)
        elif method in ("POST", "PUT", "DELETE"):
            if "write" not in scope:
                raise RESTException(f"Invalid scope for method {method}", 403)
        else:
            raise RESTException("Method not allowed", 405)

    def _get_user(self, request):
        if "SS_OAUTH_USER" not in request.META:
            raise RESTException(
                "missing oauth user - improper auth backend?", 400
            )
        username = request.META["SS_OAUTH_USER"]

        user = User.objects.get(username=username)

        return user
