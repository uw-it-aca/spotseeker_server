from django.http import HttpResponse
from django.utils.importlib import import_module
import spotseeker_server.auth.all_ok

try: from functools import wraps
except ImportError: from django.utils.functional import wraps # Python 2.4 fallback

from django.conf import settings

def app_auth_required(func):
    if hasattr(settings, 'SPOTSEEKER_AUTH_MODULE'):
        module = settings.SPOTSEEKER_AUTH_MODULE;
        try:
            mod = import_module(module)
        except ImportError, e:
            raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                       (module, e))

        try:
            method = getattr(mod, "authenticate_application")
        except AttributeError:
            raise ImproperlyConfigured('Module "%s" does not define a "authenticate_application" method.' % module)

        return method(func)
    else:
        return spotseeker_server.auth.all_ok.authenticate_application(func)

def user_auth_required(func):
    if hasattr(settings, 'SPOTSEEKER_AUTH_MODULE'):
        module = settings.SPOTSEEKER_AUTH_MODULE;
        try:
            mod = import_module(module)
        except ImportError, e:
            raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                       (module, e))

        try:
            method = getattr(mod, "authenticate_user")
        except AttributeError:
            raise ImproperlyConfigured('Module "%s" does not define a "authenticate_user" method.' % module)

        return method(func)
    else:
        return spotseeker_server.auth.all_ok.authenticate_user(func)


