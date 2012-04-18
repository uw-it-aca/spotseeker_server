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

def authenticate_application(func):
    """
    This method wraps the view function with the method
    that actually checks the application auth
    """
    def check_app(*args, **kwargs):
        """ This always allows requests through """
        return func(*args, **kwargs)
    return wraps(func)(check_app)

def authenticate_user(func):
    """
    This method wraps the view function with the method
    that actually checks the application/user auth
    """
    def check_user(*args, **kwargs):
        """ This always allows requests through """
        return func(*args, **kwargs)
    return wraps(func)(check_user)
