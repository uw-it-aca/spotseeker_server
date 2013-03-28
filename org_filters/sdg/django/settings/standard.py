#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/settings/standard.py $
#   $Revision: 33486 $ $Date: 2013-01-11 17:05:14 -0600 (Fri, 11 Jan 2013) $

import sdg

from sdg.django.settings import _util as util

from sdg.log import init_module_logger

#   Initialize module logger.
_LOGGER = init_module_logger()

#####

def standard_settings():
    # _debug_outerframes(label='standard_settings')

#   if os.environ.get('PSGCONF_CLASS_NAME', '') in _DEVELOPMENT_CLASS_LIST:
#       pass                            # We can do something here.

    #   Dictionary to be set into settings.
    settings_dict = \
        {
        'ADMINS'                    : (),
        'DATABASES'                 : { 'default' : {} },
        'MANAGERS'                  : (),
        'DEBUG'                     : True if sdg.is_developer() else False,

        # URL prefix for admin media -- CSS, JavaScript and images. Make sure
        # to use a trailing slash.
        # Examples: "http://foo.com/media/", "/media/".
    #   'ADMIN_MEDIA_PREFIX'    : '/media/',

        'AUTHENTICATION_BACKENDS'   : \
            [
        #   'sdg.django.auth.backends.BluestemBackend',
            ],

        'INSTALLED_APPS'            : \
            [
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'sdg.django',
        #   'sdg.django.bluestem',
            ],

        # Language code for this installation. All choices can be found here:
        # http://www.i18nguy.com/unicode/language-identifiers.html
        'LANGUAGE_CODE'             : 'en-us',

        # Absolute path to the directory that holds media.
        # Example: "/home/media/media.lawrence.com/"
        'MEDIA_ROOT'                : util.media_root(),

        # URL that handles the media served from MEDIA_ROOT. Make sure to use a
        # trailing slash if there is a path component (optional in other cases).
        # Examples: "http://media.lawrence.com", "http://example.com/media/"
        'MEDIA_URL'                 : '',

        'MIDDLEWARE_CLASSES'        : \
            [
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.middleware.transaction.TransactionMiddleware',
        #   'sdg.django.auth.middleware.BluestemMiddleware',
            ],

        # Retrieve the random SECRET_KEY hash foruse by the main settings.
        'SECRET_KEY'                : util.get_secret_key(),

        # FIXME add comment here.
        'TEMPLATE_CONTEXT_PROCESSORS' : \
            [
            'django.contrib.auth.context_processors.auth',
            'django.core.context_processors.debug',
            'django.core.context_processors.i18n',
            'django.core.context_processors.media',
        #   'sdg.django.context_processors.bluestem_auth',
            ],

        'TEMPLATE_DIRS'             : util.template_dir(),

        # List of callables that know how to import templates from various
        # sources.
        'TEMPLATE_LOADERS'          : \
            [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        #   'django.template.loaders.eggs.load_template_source',
            ],

        # Local time zone for this installation. Choices can be found here:
        # http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
        # although not all choices may be available on all operating systems.
        # On Unix systems, a value of None will cause Django to use the same
        # timezone as the operating system.
        # If running in a Windows environment this must be set to the same as
        # your system time zone.
        'TIME_ZONE'                 : 'America/Chicago',

        'SITE_ID'                   : 1,

        # URL prefix for admin media -- CSS, JavaScript and images. Make sure
        # to use a trailing slash.
        # Examples: "http://foo.com/media/", "/media/".
        'STATIC_URL'                : '/media/',

        'TEMPLATE_DEBUG'            : True if sdg.is_developer() else False,

        # If you set this to False, Django will make some optimizations so as
        # not to load the internationalization machinery.
        'USE_I18N'                  : True,
        }

    settings_frame = util._get_settings_frame(doraise=True)

    #   Set keys and values into settings stack frame.
    for key, value in sorted(settings_dict.items()):
        settings_frame.f_globals[key] = value

    _LOGGER.info('done setting SDG standard settings')
    return

