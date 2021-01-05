from .base_settings.common import *
import os

ALLOWED_HOSTS = ['*']

if os.getenv("ENV") == "localdev":
    DEBUG = True
else:
    DEBUG = False

INSTALLED_APPS += [
    'oauth_provider',
    'spotseeker_server',
]

MIDDLEWARE += [
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'spotseeker_server.logger.oauth.LogMiddleware',
]

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

SPOTSEEKER_AUTH_MODULE = "spotseeker_server.auth.{}".format(os.getenv('AUTH_MODULE', 'all_ok'))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'stdout_stream': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: record.levelno < logging.WARN
        },
        'stderr_stream': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: record.levelno > logging.INFO
        }
    },
    'formatters': {
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'stdout': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'filters': ['stdout_stream']
        },
        'stderr': {
            'class': 'logging.StreamHandler',
            'stream': sys.stderr,
            'filters': ['stderr_stream']
        },
    },
    'loggers': {
        'spotseeker_server.views.share_space': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': True,
        },
        '': {
            'handlers': ['stdout', 'stderr'],
            'level': 'INFO' if os.getenv('ENV', 'dev') == 'prod' else 'DEBUG'
        }
    }
}
