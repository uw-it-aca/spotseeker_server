#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/settings/custom.py $
#   $Revision: 33486 $ $Date: 2013-01-11 17:05:14 -0600 (Fri, 11 Jan 2013) $

#   Copyright (c) 2010-2013 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

import inspect
import logging
import os
import sys

import sdg

from sdg.django.settings import _util as util
from sdg.log import init_module_logger

#   Initialize module logger.
_LOGGER = init_module_logger()

#####

class CustomSettings(object):
    '''
    Class to facilitate the management of custom settings; also controls
    customer ability to modify settings not marked as user-customizable.
    '''

    #   Set of supported overridable customer settings (initialized as None).
    _supported_setting_set          = None

    #####

    @classmethod
    def _choose_extra_settings(cls, app_name):
        '''
        Choose what directory and filename are used for extra settings file.
        '''
        #   List of paths to add when running as developer.
        _developer_settings_path_list   = \
            [
            util.get_base(),
            ]

        #   List of paths to add when running as service user.
        _service_settings_path_list     = \
            [
            os.path.join(util.get_base(), util._PATH_PART_CONFIG),
            ]

        #   Set up settings file name depending who's running
        if sdg.is_service_user():
            modname = '%s_settings_customer' % app_name
            path_list = _developer_settings_path_list
            return modname, path_list

        if sdg.is_developer():
            modname = '%s_settings_developer' % app_name
            path_list = _service_settings_path_list
            return modname, path_list

        raise ValueError('can\'t find settings; invalid home directory: %s' % \
                         sdg.get_home())

    #####

    @classmethod
    def add(cls, setting, value=None):
        '''
        Add specified setting to set of settings for which customer
        modifications are supported. If value specified, update it in
        caller's global dictionary.
        '''

        #   Configuration variables are all upper-case (with underscores);
        #   skip other attributes
        if setting != setting.upper():
            logging.error('%s is not a valid setting', setting)
            return
            
        #   If set of supported settings doesn't exist, create empty set.
        #   This is used to support applications that only want the customer
        #   setting import feature both with and without enforcing that
        #   such customer setting files don't contain changes to settings
        #   not supported by SDG.
        #
        #   Applications that wish to import customer settings without
        #   enforcing "supported" settings need do nothing other than list
        #   default settings in the <appname>_settings_customer.py (and
        #   <appname>_settings_developer.py) files.
        #
        #   Applications that wish to import customer settings *with* support
        #   for enforcing "supported" settings should invoke the add_list()
        #   and/or add() methods in the settings.py file for all settings
        #   that it is desired to treat as "supported".
        if not cls._supported_setting_set:
            cls._supported_setting_set = set()
            
        #   Add to set of supported settings.
        cls._supported_setting_set.add(setting)

        #   If value specified, set value in caller's global dictionary
        if value:
            #   Get caller's global dictionary and update specified setting.
            caller_dict = inspect.currentframe().f_back.f_globals
            caller_dict[setting] = value

        return

    #####

    @classmethod
    def add_list(cls, *setting_list):
        '''
        Add specified list of settings as supporting customer modifications.
        Calls add().
        '''

        map(cls.add, setting_list)
        return

    #####

    @classmethod
    def import_settings(cls, app_name=None):
        '''Choose settings file to append to default settings file.'''

        #   Get caller's global dictionary.
        caller_dict = inspect.currentframe().f_back.f_globals

        #   If app_name not provided, get module name from caller's file path.
        if not app_name:
            app_name = os.path.basename \
                            (os.path.dirname(caller_dict['__file__']))

        logging.debug('looking for settings for application %s', app_name)

        #   Save sys.path value to a new list so that it can be restored later
        path_save       = list(sys.path)

        #   Set up settings file name depending who's running
        extra_settings_modname, path_list = cls._choose_extra_settings(app_name)

        sys.path = path_list + sys.path

        try:
            #   Import customer settings module
            extra_settings_module = __import__(extra_settings_modname)
            
            #   Restore original sys.path value
            sys.path        = path_save

        except ImportError:
            logging.info('settings file not found: %s', extra_settings_modname)

            #   Restore original sys.path value
            sys.path        = path_save
            return

        #   Iterate over settings in imported module.
        for setting in sorted(dir(extra_settings_module)):
            #   Configuration variables are all upper-case (with underscores);
            #   skip other attributes
            if setting != setting.upper():
                continue
            
            #   If _supported_setting_set is None, no settings have been 
            #   set as "supported"; therefore, we don't validate any settings 
            #   with respect to their "supported" status.
            #
            #   However, if *any* settings have been set as "supported",
            #   each setting is then validated against the set of settings
            #   so marked.
            if cls._supported_setting_set and \
               setting not in cls._supported_setting_set:
                logging.info('changes to setting \'%s\' not allowed', setting)
                continue

            #   Retrieve setting value from customer settings module
            value = getattr(extra_settings_module, setting)

            #   Set attribute on both application settings and current settings
            #   TODO Help make setting appear in output from 
            #   'manage.py diffsettings'.
        #   logging.debug('%-24s = %s' % (setting, value))
            caller_dict[setting] = value
        
        return

#####

def get_setting_names(mod):
    '''Get defined setting names and return a list.'''
    return [ k for k in sorted(dir(mod)) if k == k.upper() ]

#####

def get_setting_values(mod):
    '''Get defined settings and return a list of (name, value) tuples.'''
    return [ (k, getattr(mod, k)) for k in sorted(dir(mod)) if k == k.upper() ]
