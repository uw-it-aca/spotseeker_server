#from spotseeker_server.defaults import *
from spotseeker_server.default_forms.spot import DefaultSpotForm
from django.utils.importlib import import_module
from django.conf import settings


class SpotForm(object):
    def __new__(*args, **named_args):

        if hasattr(settings, 'SPOTSEEKER_SPOT_FORM'):
            # This is all taken from django's static file finder
            module, attr = settings.SPOTSEEKER_SPOT_FORM.rsplit('.', 1)
            try:
                mod = import_module(module)
            except ImportError, e:
                raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                           (module, e))
            try:
                FormModule = getattr(mod, attr)
            except AttributeError:
                raise ImproperlyConfigured('Module "%s" does not define a "%s" '
                                   'class.' % (module, attr))

            return FormModule(args[1])
        else:
            return DefaultSpotForm(args[1])
