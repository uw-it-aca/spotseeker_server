import os
from google.oauth2 import service_account
from .base_settings.common import *

if os.getenv("ENV", "localdev") == "localdev":
    DEBUG = True
else:
    DEBUG = False

INSTALLED_APPS += [
    "spotseeker_server",
    "oauth2_provider",
    "corsheaders",
]

MIDDLEWARE += [
    "spotseeker_server.logger.oauth.LogMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

AUTH_USER_MODEL = "spotseeker_server.Client"

AUTHENTICATION_BACKENDS = (
    "oauth2_provider.backends.OAuth2Backend",
    "django.contrib.auth.backends.ModelBackend",
)

# TODO: remove? registration should be done through the manager,
# not logging in to the admin
LOGIN_URL = '/admin/login/'

if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True
else:
    CORS_ORIGIN_ALLOW_ALL = False
    CORS_ALLOWED_ORIGINS = [  # TODO: move to env var?
        "https://scout.uw.edu",
        "https://manager.scout.uw.edu",
        # TODO: not the best idea to do it like this, but it works for now
        "https://test.scout.uw.edu",
        "https://test.manager.scout.uw.edu",
    ]

# django storages settings
if not DEBUG:
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    GS_FILE_OVERWRITE = False
    GS_BUCKET_NAME = os.getenv("STORAGE_BUCKET_NAME", "")
    GS_PROJECT_ID = os.getenv("STORAGE_PROJECT_ID")
    GS_LOCATION = os.path.join(os.getenv("ENV"), "api")
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        "/gcs/credentials.json"
    )

SPOTSEEKER_AUTH_MODULE = "spotseeker_server.auth.{}".format(
    os.getenv("AUTH_MODULE", "all_ok")
)
# turn string of auth admins into list
SPOTSEEKER_AUTH_ADMINS = (
    os.getenv("SPOTSEEKER_AUTH_ADMINS", "").replace(" ", "").split(",")
)

# Custom validation can be added by adding SpotForm and ExtendedInfoForm to
# org_forms and setting them here.
SPOTSEEKER_SEARCH_FILTERS = ["spotseeker_server.org_filters.uw_search.Filter"]
SPOTSEEKER_SPOT_FORM = "spotseeker_server.org_forms.uw_spot.UWSpotForm"
SPOTSEEKER_SPOTEXTENDEDINFO_FORM = (
    "spotseeker_server.org_forms.uw_spot.UWSpotExtendedInfoForm"
)

SPOTSEEKER_TECHLOAN_UPDATER = {
    "server_host": os.getenv("SPOTSEEKER_WEB_SERVER_HOST"),
    "oauth_key": os.getenv("SPOTSEEKER_WEB_OAUTH_KEY"),
    "oauth_secret": os.getenv("SPOTSEEKER_WEB_OAUTH_SECRET"),
    "oauth_user": os.getenv("SPOTSEEKER_WEB_OAUTH_USER"),
}

SPOTSEEKER_TECHLOAN_URL = os.getenv("SPOTSEEKER_TECHLOAN_URL")

if DEBUG:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
else:
    # The various MEMCACHED variables are set in django-container's
    # base_settings/common.py
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
            'LOCATION': MEMCACHED_SERVERS,
        }
    }
