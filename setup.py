#!/usr/bin/env python

from distutils.core import setup

setup(
    name="SpaceScout-Server",
    version="1.0",
    description="REST Backend for SpaceScout",
    install_requires=[
        "Django==1.11.*",
        "future",
        "mock<=1.0.1",
        "oauthlib==3.1.*",
        "requests==2.26.*",
        "requests-oauthlib==1.3.*",
        "Pillow",
        "pylibmc",  # switch to what django-container uses upon upgrade
        "pyproj",
        "pytz",
        "simplejson>=2.1",
        "django-oauth-plus@git+https://github.com/edx-unsupported/django-oauth-plus#egg=2.2.9.edx-4",
        "django-storages[google]",
        "schema",
        "six",
        "phonenumbers",
        "responses",
    ],
)
