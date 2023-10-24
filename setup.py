#!/usr/bin/env python

from distutils.core import setup

setup(
    name="SpaceScout-Server",
    version="1.0",
    description="REST Backend for SpaceScout",
    install_requires=[
        "Django==2.2.*",
        "future",
        "mock",
        "oauthlib==3.1.*",
        "django-oauth-toolkit",
        "django-cors-headers==3.10.*",
        "requests",  # TODO: test with live scout, scout-manager, techloan
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
