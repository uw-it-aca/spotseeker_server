#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/settings/_util.py $
#   $Revision: 33486 $ $Date: 2013-01-11 17:05:14 -0600 (Fri, 11 Jan 2013) $

#   Copyright (c) 2013 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''
Package of SDG Django-related functions.
'''

import inspect
import logging
import os
import sys

from django.conf import settings

import sdg

from sdg.log import StreamLog, init_module_logger

#   Initialize module logger.
_LOGGER = init_module_logger()

#   Used to check contents of PSGCONF_CLASS_NAME environment variable.
_DEVELOPMENT_CLASS_LIST = [ 'Development' ]

_PATH_PART_CONFIG       = 'var/config'
_PATH_PART_WEB          = 'public_html/https'

#####

def get_base():
    # _debug_outerframes(label='get_base')

    base_dir = os.environ.get('PROJECT_ROOT_DIRECTORY', '')

    if base_dir:
        return base_dir

    settings_frame = _get_settings_frame()

    if settings_frame:
        base_dir = settings_frame.f_globals.get('PROJECT_ROOT_DIRECTORY', '')

        if base_dir:
            return base_dir

    return sdg.get_home()

#####

#   TODO needs lots of boilerplate.
def get_secret_key():
    #   Get secret key from configuration directory.
    path = os.path.join(get_base(), _PATH_PART_CONFIG, 'secret_key')
    _LOGGER.debug('looking for secret key in %s' % path)

    try:
        return open(path, 'r').read()
        
    except:
        pass

    return None

#####

def media_root():
    '''
    Return a media root based on whether caller is service user or developer.
    '''
    if sdg.is_service_user():
        return os.path.join(get_base(), _PATH_PART_WEB, 'static')
    
    #   Get __file__ attribute from caller's frame.
    ##### FIXME
    dir = os.path.dirname \
            (inspect.currentframe().f_back.f_globals.get('__file__'))
    return os.path.abspath(os.path.join(dir, '../../web/static'))

#####

def show_settings():
    settings_frame = _get_settings_frame(doraise=True)

    for key, value in sorted(settings_frame.f_globals.items()):
        if key.upper() != key:
            continue

        _LOGGER.debug('%-28s = %s' % (key, value))

    return

#####

def template_dir():
    '''
    Return a tuple of template directories based on whether caller is
    service user or deveeloper.
    '''
    if sdg.is_service_user():
        return (os.path.join(get_base(), _PATH_PART_WEB, 'template'), )

    #   Get __file__ attribute from caller's frame.
    ##### FIXME
    dir = os.path.dirname \
            (inspect.currentframe().f_back.f_globals.get('__file__'))
    return (os.path.abspath(os.path.join(dir, '../../web/template')), )

#####

def _debug_outerframes(label=''):
    if label:
        print '----- BEGIN %s' % label

    outerframes = inspect.getouterframes(inspect.currentframe().f_back)

    context = outerframes[0][4]
    if context:
        for line in context:
            print ':\t%s' % line

    for frame, filename, lineno, function, code_context, index in outerframes:
        name = getattr(inspect.getmodule(frame), '__name__', None)
        print '\t%-24s %-20s %3d %s' % (name, function, lineno, filename)

    if label:
        print '----- END   %s' % label

    return
    
#####

def _get_settings_frame(doraise=False):
    '''
    Analyze outer frames to ensure this is called from settings module.
    '''
    # _debug_outerframes(label='_get_settings_frame')

    outerframes = inspect.getouterframes(inspect.currentframe())
    for frame, filename, lineno, function, code_context, index in outerframes:
        if inspect.getmodule(frame).__name__ == 'settings':
            return frame

    if doraise:
        raise Exception('couldn\'t find settings module in outer frames')

    return None
