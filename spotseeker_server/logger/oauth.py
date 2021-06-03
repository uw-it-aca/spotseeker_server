# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" This creates a log along the lines of the apache
    common log format, but with info about the OAuth apps.
    This is the format:

    [timestamp] app_pk\t"app_name"\tuser_name\t"METHOD URI"
    response_status response_size
"""

from django.utils.deprecation import MiddlewareMixin
from datetime import datetime
import logging


class LogMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def process_response(self, request, response):
        request_uri = request.get_full_path()
        request_method = request.META["REQUEST_METHOD"]

        response_status = response.status_code

        # response.content will empty out the FileWrapper object
        # on file downloads - those views need to correctly set
        # their own content length
        if "Content-Length" in response:
            response_length = response["Content-Length"]
        else:
            response_length = len(response.content)

        oauth_app_pk = "-"
        oauth_app_name = "-"
        oauth_user = "-"

        if "SS_OAUTH_USER" in request.META:
            oauth_user = request.META["SS_OAUTH_USER"]
        if "SS_OAUTH_CONSUMER_PK" in request.META:
            oauth_app_pk = request.META["SS_OAUTH_CONSUMER_PK"]
        if "SS_OAUTH_CONSUMER_NAME" in request.META:
            oauth_app_name = request.META["SS_OAUTH_CONSUMER_NAME"]

        timestamp = datetime.now().strftime("%d/%b/%Y %H:%M:%S")

        log_message = '[{0}] {1}\t"{2}"\t{3}\t"{4} {5}" ' "{6} {7}".format(
            timestamp,
            oauth_app_pk,
            oauth_app_name,
            oauth_user,
            request_method,
            request_uri,
            response_status,
            response_length,
        )

        self.logger.info(log_message)

        return response
