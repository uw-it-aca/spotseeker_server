#!/usr/bin/env python

from distutils.core import setup

setup(
    name="SpaceScout-Server",
    version="1.0",
    description="REST Backend for SpaceScout",
    install_requires=[
        "Django==2.2.*",
        "future",
        "mock<=1.0.1",
        "oauthlib==3.1.*",
        "django-oauth-toolkit",
        "requests==2.26.*",
        "requests-oauthlib==1.3.*",
        "Pillow",
        "pylibmc",  # switch to what django-container uses upon upgrade
        "pyproj",
        "pytz",
        "simplejson>=2.1",
        "django-storages[google]",
        "schema",
        "six",
        "phonenumbers",
        "responses",
    ],
)
