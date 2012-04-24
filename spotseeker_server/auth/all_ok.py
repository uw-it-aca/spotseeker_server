"""
This module will allow all requests, without requiring authentication or
authorization.  To use it, add this to your settings.py:

SPOTSEEKER_AUTH_MODULE = spotseeker_server.auth.all_ok
"""

def authenticate_application(*args, **kwargs):
    """ This always allows requests through """
    return


def authenticate_user(*args, **kwargs):
    """ This always allows requests through """
    return
