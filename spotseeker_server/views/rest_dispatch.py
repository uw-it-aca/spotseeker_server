""" Copyright 2012-2014 UW Information Technology, University of Washington

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
import simplejson as json
import traceback


class JSONResponse(HttpResponse):
    """
    A standard HttpResponse that will serialize the body to JSON
    and set the content-type to 'application/json'
    """

    def __init__(self, content='', *args, **kwargs):
        if content != '':
            if settings.DEBUG and settings.JSON_PRETTY_PRINT:
                content = json.dumps(content, sort_keys=True, indent=4 * ' ')
            else:
                content = json.dumps(content)

        if not kwargs.get('content_type', None):
            kwargs['content_type'] = 'application/json'

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
    """ Handles passing on the request to the correct view method based on the request type.
    """

    def run(self, *args, **named_args):
        request = args[0]
        method = request.META['REQUEST_METHOD']

        try:
            if "GET" == method and hasattr(self, "GET"):
                response = self.GET(*args, **named_args)
            elif "POST" == method and hasattr(self, "POST"):
                response = self.POST(*args, **named_args)
            elif "PUT" == method and hasattr(self, "PUT"):
                response = self.PUT(*args, **named_args)
            elif "DELETE" == method and hasattr(self, "DELETE"):
                response = self.DELETE(*args, **named_args)
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

        if getattr(settings, 'DEBUG', False):
            json_values['stack'] = traceback.format_exc().splitlines()

        return json_values

    def validate_etag(self, request, obj):
        if not "HTTP_IF_MATCH" in request.META:
            if not "If_Match" in request.META:
                raise RESTException("If-Match header required", 400)
            else:
                request.META["HTTP_IF_MATCH"] = request.META["If_Match"]

        if request.META["HTTP_IF_MATCH"] != obj.etag:
            raise RESTException("Invalid ETag", 409)

    def _get_user(self, request):
        if not 'SS_OAUTH_USER' in request.META:
            print request.META
            raise Exception("missing oauth user - improper auth backend?")
        username = request.META['SS_OAUTH_USER']

        user = User.objects.get(username=username)

        return user
