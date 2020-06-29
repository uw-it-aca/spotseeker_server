from importlib import import_module
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class EnforceSettingName(type):
    """
    Metaclass to prevent creation of loaders that do not specify setting_name
    """
    def __init__(self, name, bases, attrs):
        super(EnforceSettingName, self).__init__(name, bases, attrs)
        if self.setting_name is None and name != 'ModuleObjectLoader':
            raise Exception('Module loader %s did not specify setting_name'
                            % name)


class ModuleObjectLoader(object):
    """
    Generic loader class that centralizes the copy-pasted code found in
    all the forms loaders. Loaders should subclass this and specify
    setting_name and optionally a default.
    """
    __metaclass__ = EnforceSettingName

    setting_name = None
    default = None

    @classmethod
    def implementation(cls, *args, **kwargs):
        # Get the value from settings
        setting = getattr(settings, cls.setting_name, None)
        if setting is None:
            # Setting was not specified. Return the default if possible,
            # otherwise tell user to add the setting.
            if cls.default is None:
                raise ImproperlyConfigured('You need to specify %s in your '
                                           'settings' % cls.setting_name)
            else:
                return cls.default

        else:
            # Setting was specified. Split into module + attribute name
            return load_object_by_name(setting)

    def __new__(cls, *args, **kwargs):
        return cls.implementation()(*args, **kwargs)


def load_module_by_name(mod_name):
    """Load a module by name"""
    try:
        return import_module(mod_name)
    except ImportError as e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                   (mod_name, e))


def load_object_by_name(object_name):
    """Load an object from a module by name"""
    mod_name, attr = object_name.rsplit('.', 1)
    mod = load_module_by_name(mod_name)
    try:
        return getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module %s does not define %s' %
                                   (mod_name, attr))
