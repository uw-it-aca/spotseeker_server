#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/log/levels.py $
#   $Revision: 31262 $ $Date: 2012-07-17 12:47:23 -0500 (Tue, 17 Jul 2012) $

#   Copyright (c) 2011, 2012 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''Custom SDG log levels used in conjunction with Python logging.'''

import logging

#####

#   pylint: disable=R0903
class LogLevel(object):
    '''Custom log level class.'''

    _init   = False

    #   Dictionary of custom levels used by CITES SDG modules.
    _sdg_level_dict = \
        {
        'SDG_DEBUG_1'   : 8,
        'SDG_DEBUG_2'   : 7,
        'SDG_DEBUG_3'   : 6,
        }

    #####

    @classmethod
    def initialize(cls):
        '''Initialize custom log levels.'''

        #   Don't repeat initialization.
        if cls._init:
            return

        #####

        def _make_logger(level):
            '''Return a function that logs at the specified level.'''
        
            #####

            def log_func(msg, *args, **kwargs):
                '''Closure used in the creation of logging function.'''
                return logging.log(level, msg, *args, **kwargs)
        
            return log_func

        #   Iterate over custom log levels.
        for level_name, level in cls._sdg_level_dict.items():
            #   Add level name for custom level.
            logging.addLevelName(level, level_name.upper())
        
            #   Add attribute for custom level to allow using references like
            #   "logging.CUSTOM_LEVEL".
            setattr(logging, level_name.upper(), level)
        
            #   Add method for custom level to allow using method calls like
            #   "logging.custom_level(msg, *args, **kwargs)".
            setattr(logging, level_name.lower(), _make_logger(level))

        #   Flag initialization as complete.
        cls._init = True
        return

#   Initialize custom log levels.
LogLevel.initialize()
