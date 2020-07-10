from .base_settings.common import *
import os

ALLOWED_HOSTS = ['*']

if os.getenv("ENV") == "localdev":
    DEBUG = True
else:
    DEBUG = False

INSTALLED_APPS += [
    'oauth2_provider',
    'spotseeker_server',
]

MIDDLEWARE += [
    'django.contrib.auth.middleware.RemoteUserMiddleware',
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

OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
        'is_trusted': 'Trusted scope',
        'bypasses_user_authorization': 'Bypass User Auth-z scope',
    },
}

OAUTH2_MODE = {
    'MOCK': True,
    'SCOPES': [],
}