#!/usr/bin/env python

from distutils.core import setup

setup(name='SpaceScout-Server',
      version='1.0',
      description='REST Backend for SpaceScout',
      install_requires=['Django>=1.4,<1.5','mock','oauth2','PIL','pyproj','pytz','South','simplejson>=2.1','django-oauth-plus'],
     )
