"""
This module uses oauth to allow applications and users access.
Supports 2-legged oauth for application requests, and for trusted
applications accessing user-restricted methods.  Supports 3-legged
oauth for non-trusted applications that want to access user methods.

To use this module, add this to your settings.py:

SPOTSEEKER_AUTH_MODULE = spotseeker_server.auth.oauth

"""
from django.http import HttpResponse

from oauth_provider.utils import get_oauth_request, verify_oauth_request
from oauth_provider.store import store, InvalidConsumerError, InvalidTokenError

# w/ Python 2.4 fallback
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps

def authenticate_application(func):
    def check_app(*args, **kwargs):
        request = args[1]
        try:
            oauth_request = get_oauth_request(request)
            consumer = store.get_consumer(request, oauth_request, oauth_request['oauth_consumer_key'])
            verify_oauth_request(request, oauth_request, consumer)

            return func(*args, **kwargs)
        except Exception as e:
            response = HttpResponse("Error authorizing application")
            response.status_code = 401
            return response
    return wraps(func)(check_app)

def authenticate_user(func):
    def check_user(*args, **kwargs):
        request = args[1]
        try:
            oauth_request = get_oauth_request(request)
            consumer = store.get_consumer(request, oauth_request, oauth_request['oauth_consumer_key'])
            verify_oauth_request(request, oauth_request, consumer)

            # XXX - if consumer is trusted, return here

            access_token = store.get_access_token(request, oauth_request, consumer, oauth_request[u'oauth_token'])
            user = store.get_user_for_access_token(request, oauth_request, access_token)

            return func(*args, **kwargs)
        except Exception as e:
            response = HttpResponse("Error authorizing application")
            response.status_code = 401
            return response
    return wraps(func)(check_user)
