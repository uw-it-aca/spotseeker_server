#!/usr/bin/env python

from distutils.core import setup

setup(name='SpaceScout-Server',
      version='1.0',
      description='REST Backend for SpaceScout',
      install_requires=[
                        'Django<1.9,>=1.7',
                        'mock<=1.0.1',
                        'oauth2<=1.5.211',
                        'Pillow',
                        'pyproj',
                        'pytz',
                        'simplejson>=2.1',
                        'django-oauth-plus<=2.2.5',
                        'phonenumbers'
                       ],
     )
