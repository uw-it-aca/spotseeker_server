#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/auth/backends.py $
#   $Revision: 29352 $ $Date: 2012-04-23 15:45:00 -0500 (Mon, 23 Apr 2012) $

#   Copyright (c) 2010 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''Package of SDG custom authentication backends for Django.'''

import logging
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

from sdg.django.auth import BluestemData

class BluestemBackend(ModelBackend):
    '''Class implementing Bluestem authentication backend.'''

    #####

    def authenticate(self, bluestem_data=None):
        '''Authenticate Bluestem credentials, returning user object or None.'''

        #   Return if Bluestem data is missing or invalid 
        if not bluestem_data or not isinstance(bluestem_data, BluestemData):
            logging.error('bad object handed to authenticate()')
            return None

        auth    = None
        domain  = None

        try:
            #   Retrieve auth method and domain from settings
            auth   = settings.BLUESTEM_AUTH
            domain = settings.BLUESTEM_DOMAIN

            #   Raise AttributeError if either auth or domain are empty
            if not auth or not domain:
                raise AttributeError

        except AttributeError:
            #   AttributeError raised if either auth or domain don't exist
            #   or if they consist of an empty string
            logging.error \
                ('BLUESTEM_AUTH or BLUESTEM_DOMAIN settings not specified')
            return None                 # Auth and domain not specified

        #   Bluestem auth and domain must match value in settings file
        if bluestem_data.auth   != auth or \
           bluestem_data.domain != domain:
            logging.error \
                ('unsupported Bluestem authentication method or domain: %s',
                 bluestem_data)
            return None                 # Wrong auth method or domain

        username = self.clean_username(bluestem_data.user)

        try:
            #   Look for exact match of username in Django's auth database
            user = User.objects.get(username__exact=username)

        except User.DoesNotExist:
            return None                 # No such user

        return user                     # Found matching user

    #####

    def clean_username(self, username):
        """
        Performs any cleaning on the "username" prior to using it to get or
        create the user object.  Returns the cleaned username.

        By default, returns the username unchanged.
        """
        return username

    #####

    def configure_user(self, user):
        """
        Configures a user after creation and returns the updated user.

        By default, returns the user unmodified.
        """
        return user
