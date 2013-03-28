# $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/auth/__init__.py $
#   $Revision: 29352 $ $Date: 2012-04-23 15:45:00 -0500 (Mon, 23 Apr 2012) $

#   Copyright (c) 2010 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''Package for SDG custom authentication methods for Django.'''

import re
import sys

from types import DictType

from django.core.exceptions import ValidationError

#   Compiled regular expression validation patterns
_RE_ALNUM   = re.compile('^[\-a-z0-9]+$')
_RE_DOMAIN  = re.compile('^([\-\.A-Za-z0-9]+)$')
_RE_FULL_ID = re.compile('^([\-a-z0-9]+)@([\-\.a-z0-9]+)/([\-a-z0-9]+)$')
_RE_PART_ID = re.compile('^([\-a-z0-9]+)(@([\-\.a-z0-9]+))?(/([\-a-z0-9]+))?$')
_RE_NUM     = re.compile('^[0-9]+$')

#   mod_bluestem adds the following keys to the CGI environment, which winds
#   up in request.META:
#
#   VARIABLE                VALUE
#   ------------------------------------------------
#   BLUESTEM_ID             short form of Bluestem ID
#   BLUESTEM_ID_FULL        full form of Bluestem ID
#   BLUESTEM_ID_USER        user component of Bluestem ID
#   BLUESTEM_ID_DOMAIN      domain component of Bluestem ID
#   BLUESTEM_ID_AUTH        auth method component of Bluestem ID
#   BLUESTEM_IDLE_TIME      idle time (in seconds)
#   BLUESTEM_SESSION_TIME   session time (in seconds)
    
_BLUESTEM_ENV_DICT = \
    {
    'BLUESTEM_ID'           : ('short',         _RE_PART_ID),
    'BLUESTEM_ID_AUTH'      : ('auth',          _RE_ALNUM),
    'BLUESTEM_ID_DOMAIN'    : ('domain',        _RE_DOMAIN),
    'BLUESTEM_ID_USER'      : ('user',          _RE_ALNUM),
    'BLUESTEM_ID_FULL'      : ('full',          _RE_FULL_ID),
    'BLUESTEM_IDLE_TIME'    : ('idle_time',     _RE_NUM),
    'BLUESTEM_SESSION_TIME' : ('session_time',  _RE_NUM),
    }

#   Default logout path for Bluestem
BLUESTEM_LOGOUT_PATH    = '/bluestem/logout.cgi'

#####

class BluestemData(object):
    '''Class used to store Bluestem credentials provided by mod_bluestem.'''

    #####

    def __init__(self, env):
        '''Initialize Bluestem object from data in environment.'''

        #   Shuts up pylint.
        self.full   = None

        try:
            #   Raise TypeError if  parameter isn't a dictionary.
            if env is None or not isinstance(env, DictType):
                raise TypeError('expecting dictionary; got %s' % \
                                env.__class__.__name__)

            #   Iterate over expected environment variables and validate 
            #   their value.
            for env_name, bluestem_tuple in _BLUESTEM_ENV_DICT.items():
                #   Retrieve name of target attribute and compiled regular
                #   expression validator pattern.
                attr_name, attr_re = bluestem_tuple[:]
                value = env[env_name]

                #   Raise KeyError if environment variable is empty or invalid.
                if not value or (attr_re and not attr_re.search(value)):
                    raise KeyError

                #   Set attribute; raises KeyError if variable missing.
                setattr(self, attr_name, value)

        except KeyError:
            #   Raise exception for one or more bad environment variables.
            raise ValidationError('Missing or invalid Bluestem environment')

        return                          # BluestemData object initialized

    #####

    def __str__(self):
        '''Default string representation is full Bluestem ID.'''
        return u'%s' % self.full
