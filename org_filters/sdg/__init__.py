#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/__init__.py $
#   $Revision: 33391 $ $Date: 2012-12-21 10:49:02 -0600 (Fri, 21 Dec 2012) $

#   Copyright (c) 2010 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''
General-purpose utilities for CITES Software Development Group applications.
'''

from __future__ import absolute_import

import logging
import os
import posix
import re
import sys

from sdg import log

#   Directory (relative to home) to which log files are written.
_LOG_SUBDIR             = 'var/log'

#   Path in which developer directories reside.
_PATH_DEVELOPER         = '/home'

#   Path in which service directories reside.
_PATH_SERVICE           = '/services'

#   Path (relative to home) win which service-specific Python module resides.
_SERVICE_PYTHON_SUBDIR  = 'share/python' 

#   List of paths to be appended to sys.path if they exist.
_PATH_LIST = \
    [
    ]

#   Public class members

VERBOSE = 0                     # Verbosity level for sdg package

#   Initialize module logger.
#   NOTE: This is a top-level logger that does NOT propagate upward.
LOGGER = log.init_module_logger(top=True)

#####

def set_settings_module():
    '''
    Try to find settings module and set its Python path into the environment.
    '''

    #   Don't do anything if already set.
    if os.environ.get('DJANGO_SETTINGS_MODULE', None):
        return None

    #   If not service user, can't do anything. Developer has other 
    #   alternatives.
    if not is_service_user():
        return None

    #   Determine path of service-specific Python directory.
    home_lib = os.path.join(get_home(), _SERVICE_PYTHON_SUBDIR)
    
    settings_set = []

    #   Iterate over directory tree rooted at service-specific Python directory.
    for dir_path, dir_list, file_list in os.walk(home_lib):
        for settings_file in file_list:
            #   Look for settings.py or settings.pyc; skip non-matching files.
            if not re.search('^(settings)\.pyc?$', settings_file):
                continue

            #   Construct Python name of settings module and append to list.
            settings = '%s.settings' % os.path.basename(dir_path)
            settings_set.append(settings)

        #   Don't traverse levels deeper than one level below top.
        if os.path.dirname(dir_path) == home_lib:
            dir_list[:] = []

    #   Must have exactly one setting path to succeed.
    if len(settings_set) != 1:
        raise Exception('unable to find settings module')

    #   Set setting module into environment.
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_set[0]
    return None

#####

def get_home():
    '''
    Return home directory if present in environment. Shortcut to using
    os.environ['HOME'].  Looks up home directory from password file if
    HOME not set or invalid.
    '''
    if 'HOME' not in os.environ or os.environ['HOME'] in ('', '/'):
        import pwd
        os.environ['HOME'] = pwd.getpwuid(os.getuid()).pw_dir

    return os.environ['HOME']

#####

def is_developer():
    '''Returns True if home directory implies that caller is a developer.'''
    prefix =  os.path.commonprefix((get_home(), _PATH_DEVELOPER))
    return (prefix == _PATH_DEVELOPER)

#####

def is_service_user():
    '''Return true if home directory implies that caller is a service user.'''
    prefix =  os.path.commonprefix((get_home(), _PATH_SERVICE))
    return (prefix == _PATH_SERVICE)

#####

def is_interactive():
    '''Return true if run from an interactive session.'''
    try:
        tty = open('/dev/tty')

        tpgrp = posix.tcgetpgrp(tty.fileno())
        pgrp  = posix.getpgrp()

        tty.close()

        return (tpgrp == pgrp)

    except IOError:
        return False

#####

def set_standard_path():
    '''Set standard paths for SDG development projects.'''

    #   Get home directory (more reliably than via sys.environ['HOME']).
    home = get_home()

    #   If service user, append standard python library directory to list
    #   of paths to be appended to sys.path.
    if is_service_user():
        home_lib = os.path.join(home, _SERVICE_PYTHON_SUBDIR)
    
        if home_lib not in _PATH_LIST:
            _PATH_LIST.append(home_lib)

    #   For every path to be added, append to sys.path if not already present
    #   and if path exists on fileysstem.
    for path in _PATH_LIST:
        if path not in sys.path and os.path.isdir(path):
            sys.path.append(path)

    return sys.path
