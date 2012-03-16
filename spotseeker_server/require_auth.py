from django.http import HttpResponse

try: from functools import wraps
except ImportError: from django.utils.functional import wraps # Python 2.4 fallback

# By default this should load the 2-legged oauth method.
def app_auth_required(func):
    def _checkApp(*list_args, **named_args):
        auth_ok = True
        if auth_ok:
            return func(*list_args, **named_args)
        else:
            return HttpResponse("App not authorized")

    return wraps(func)(_checkApp)

# By default this should load the 3-legged oauth method.
def user_auth_required(func):
    def _checkUser(*list_args, **named_args):
        auth_ok = True
        if auth_ok:
            return func(*args, **what)
        else:
            return HttpResponse("User and/or App not authorized")

    return wraps(func)(_checkUser)
