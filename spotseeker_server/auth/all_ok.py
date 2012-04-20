"""
This module will allow all requests, without requiring authentication or
authorization.  To use it, add this to your settings.py:

SPOTSEEKER_AUTH_MODULE = spotseeker_server.auth.all_ok
"""

# w/ Python 2.4 fallback
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps

def authenticate_application(*args, **kwargs):
    """ This always allows requests through """
    return

def authenticate_user(*args, **kwargs):
    """ This always allows requests through """
    return
