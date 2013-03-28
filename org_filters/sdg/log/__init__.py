#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/log/__init__.py $
#   $Revision: 33466 $ $Date: 2013-01-08 17:16:28 -0600 (Tue, 08 Jan 2013) $

#   Copyright (c) 2011 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''Logging utility classes and functions.'''

import inspect  
import logging
import os
import sys
import types

from copy import deepcopy
from logging.handlers import SysLogHandler

#   Default address for constructing logging.handlers.SysLogHandler.
_SYSLOG_DEFAULT_ADDRESS     = '/dev/log'

#   Default formatter (used for non-syslog logs).
_FORMATTER_DEFAULT  = logging.Formatter \
    (
#   fmt='%(asctime)s %(module)s %(levelname)s %(message)s',
    fmt=' '.join(('%(asctime)s [%(process)s] %(name)-20s %(funcName)s',
                  '%(levelname)s %(message)s')),
    datefmt='%Y/%m/%d %H:%M:%S',
    )

#   Formatter used for syslog. (Timestamp and level are natively logged.)
_FORMATTER_SYSLOG   = logging.Formatter \
    (
#   fmt='%(module)s %(levelname)s %(message)s',
    fmt='[%(process)s] %(name)-20s %(funcName)s: %(levelname)s: %(message)s',
    )

#####

#   This class makes up for the absence of the logging.NullHandler class
#   that doesn't exist until Python 2.7.
class NullHandler(logging.Handler):
    '''
    Define NullHandler that does nothing but prevents default log
    initialization from taking place.'''
    def emit(self, record):
        '''Emit log record.'''
        pass

#####

def init_module_logger(top=False, name=None):
    '''
    Initialize logger for a library module. The 'top' keyword is used
    by top-level loggers that shouldn't propagate logging up toward the
    root logger.
    '''
    if not name:
        #   Get name of module calling this function.
        name = inspect.currentframe().f_back.f_globals.get('__name__')

    #   If root logger hasn't already been initialized, Set a null handler
    #   on the root logger to give caller opportunity to initialize logging.
    if len(logging.root.handlers) == 0:
        logging.getLogger().addHandler(NullHandler())

    #   Get logger with proper name and add null handler to it.
    logger = logging.getLogger(name)

    if top:
        logger.propagate = 0

    return logger

#   Initialize module logger.
LOGGER = init_module_logger()

#####

def log_exception(msg=None):
    '''Log exception, formatting each line from exception.'''

    import traceback

    #   Log message if present.
    if msg:
        logging.error(msg)

    #   Log each line from traceback, splitting on newline.
    [ logging.error(l) for l in traceback.format_exc().split('\n') if l ]
    return

#####

#   pylint: disable=R0903
class Log(object):
    '''Base class for log object (not intended to be instantiated directly).'''

    #   Dictionary of known loggers.
    _known_logger_set   = set()

    #   Verbosity level for module.
    verbose     = 0

    #####

    @classmethod
    def get_level_dict(cls):
        '''Get dictionary of valid log levels and their numeric values.'''

        #   Build dictionary of levels known to logging module, and build
        #   dictionary to allow looking up numeric level from key.
        level_dict = dict()

        for level in dir(logging):
            #   Skip data that's not pertinent.
            if not level.upper() == level or level == 'BASIC_FORMAT':
                continue

            #   Add numeric level with level string as key.
            level_dict[level] = getattr(logging, level)

        return level_dict

    #####

    @classmethod
    def _init(cls, handler, name=None, level=logging.INFO):
        '''Initialize log object.'''

        #   If level is provided as string, translate it to integer level.
        if isinstance(level, types.StringTypes):
            #   Get level attribute from logging object.
            #   pylint: disable=E1103
            level_num = getattr(logging, level.upper(), None)
            
            #   Error if value  doesn't translate to an integer.
            if not isinstance(level_num, int):
                raise ValueError('invalid syslog level: %s' % level)

            #   Use numeric level from here on.
            level = level_num

        #   Chicken-and-egg problem; we can't use logging since we're not
        #   yet set up.
        if Log.verbose:
            print >> sys.stderr, 'logger %s %s %s(%d)' % \
                (name if name else 'root', cls.__name__, 
                 logging.getLevelName(level), level)

        #   Get named logger or root logger in absence of name.
        logger = logging.getLogger(name)

        #   Run first-time setup for this logger.
        if logger in cls._known_logger_set:
            return logger

        #   Add to set of known loggers.
        cls._known_logger_set.add(logger)

        if Log.verbose:
            print >> sys.stderr, 'setting up logger %s' % logger

        #   Set non-root logger to not propagate upward.
        if not isinstance(logger, logging.RootLogger):
            logger.propagate = False

        #   Set appropriate formatter depending on whether object uses
        #   SysLogHandler.
        if isinstance(handler, SysLogHandler):
            #   Set formatter for SysLogHandler.
            handler.setFormatter(_FORMATTER_SYSLOG)

        else:
            #   Set formatter for other handler.
            handler.setFormatter(_FORMATTER_DEFAULT)

        #   Set level for this handler.
        handler.setLevel(level)

        #   If logger's level not yet set, do so.
        if logger.level == logging.NOTSET:
            logger.setLevel(level)

        #   Add handler to logger.
        logger.addHandler(handler)

        return logger

#####

class FileLog(Log):
    '''Class that logs to file.'''
    
    #####

    @classmethod
    def init(cls, path, name=None, level=logging.INFO):
        '''Initialize log handler.'''

        dir_path = os.path.dirname(os.path.abspath(path))

        #   Make log directory if it doesn't yet exist.
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path, 0750)

        #   Call superclass initialization method.
        return super(cls, cls)._init(logging.FileHandler(path), 
                                     name=name, level=level)

#####

#   pylint: disable=R0903
class StreamLog(Log):
    '''Class that logs to stream (e.g., sys.stdout).'''
    
    #####

    @classmethod
    def init(cls, stream=None, name=None, level=logging.INFO):
        '''Initialize log handler.'''

        #   Call superclass initialization method.
        return super(cls, cls)._init(logging.StreamHandler(stream), 
                                     name=name, level=level)

#####

import codecs

#   Provide a replacement for SysLogHandler's emit method since the version
#   shipped with Python 2.6 creates corrupt log strings due to mishandling
#   the BOM with a Unicode log record. This replacement code is lifted
#   verbatim from the Python 2.7 release.

def _fixed_syslog_emit(self, record):
    """
    Emit a record.

    The record is formatted, and then sent to the syslog server. If
    exception information is present, it is NOT sent to the server.
    """
    msg = self.format(record) + '\000'
    #   pylint: disable=W0105
    """
    We need to convert record level to lowercase, maybe this will
    change in the future.
    """
    prio = '<%d>' % self.encodePriority(self.facility,
                                        self.mapPriority(record.levelname))
    # Message is a string. Convert to bytes as required by RFC 5424
    if type(msg) is unicode:
        msg = msg.encode('utf-8')
        if codecs:
            msg = codecs.BOM_UTF8 + msg
    msg = prio + msg
    try:
        if self.unixsocket:
            try:
                self.socket.send(msg)
            #   pylint: disable=E0602
            except socket.error:
                #   pylint: disable=W0212
                self._connect_unixsocket(self.address)
                self.socket.send(msg)
        #   pylint: disable=E0602
        elif self.socktype == socket.SOCK_DGRAM:
            self.socket.sendto(msg, self.address)
        else:
            self.socket.sendall(msg)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        self.handleError(record)

#####

#   pylint: disable=R0903
class Syslog(Log):
    '''Class that logs to syslog.'''

    #####

    @classmethod
    def init(cls, facility=SysLogHandler.LOG_LOCAL0, name=None,
                  level=logging.INFO):
        '''Initialize log handler.'''

        #   If facility is provided as string, translate it to integer level.
        if isinstance(facility, types.StringTypes):
            if not facility in SysLogHandler.facility_names:
                raise ValueError('invalid syslog facility: %s' % facility)

            facility = SysLogHandler.facility_names[facility]

        #   Call superclass initialization method.
        return super(cls, cls)._init \
            (SysLogHandler(address=_SYSLOG_DEFAULT_ADDRESS, facility=facility),
             name=name, level=level)

    #   Replace SysLogHandler's emit method with one that doesn't create
    #   corrupt log messages when the log text is a unicode string.
    SysLogHandler.emit = _fixed_syslog_emit

#####

class FileLogFromConfig(object):
    '''
    Utility class for file-based log (logging.FileHandler) based on
    configuration file.
    '''
    
    _opt_valid_dict = \
        {
        'level'     : False,
        }

    #   Build dictionary of valid options based on levels known to logging
    #   module, and build dictionary to allow looking up level from level_key.
    for level in Log.get_level_dict():
        if not level.upper() == level or level == 'BASIC_FORMAT':
            continue

        #   Set name of key expected in configuration file.
        _level_key = 'log_' + level.lower()

        #   None of the level logging options are required.
        _opt_valid_dict[_level_key] = False

    #####

    @classmethod
    def init(cls, config, section='LogFile', **aux_opt_dict):
        '''Initialize log handler from sdg.config.Config object.'''

        opt_dict = config.validate_section \
                     (section, cls._opt_valid_dict, **aux_opt_dict)

        #   Dictionary of destination log paths and their levels.
        path_dict   = {}

        #   Iterate over valid configuration keys and determine which were
        #   specified in option dict.
        for opt, level in Log.get_level_dict().items():
            #   Set name of key expected in configuration file.
            opt_key = 'log_' + opt.lower()

            if opt_key not in opt_dict:
                #   Option not specified.
                continue

            #   For this option, retrieve specified path, save path and
            #   asociated level, then delete path from opt_dict for passing
            #   to superclass.
            path = opt_dict[opt_key]
            path_dict[path] = level
            del opt_dict[opt_key]

        #   For every path to which we are to log, derive the full path
        #   (expanding tildes as appropriate), and initialize handler.
        for path, level in path_dict.items():
            path = os.path.realpath(os.path.expanduser(path))

            #   Make deep copy of opt_dict so we can override its level for
            #   this path only.
            temp_dict = deepcopy(opt_dict)

            temp_dict['level'] = level
            FileLog.init(path, **temp_dict)

        return

#####

class StreamLogFromConfig(object):
    '''
    Utility class for stream-based log (logging.StreamLogHandler) based on
    configuration file.
    '''
    
    _opt_valid_dict = \
        {
        'level'     : False,
        }

    #####

    @classmethod
    def init(cls, config, section='Log', **aux_opt_dict):
        '''Initialize log handler from sdg.config.Config object.'''

        opt_dict = config.validate_section \
                    (section, cls._opt_valid_dict, **aux_opt_dict)

        StreamLog.init(**opt_dict)

#####

class SyslogFromConfig(object):
    '''
    Utility class for file-based log (logging.handlers.SysLogHandler) based on
    configuration file.
    '''
    
    _opt_valid_dict = \
        {
        'facility'      : False,
        'level'         : False,
        }

    #####

    @classmethod
    def init(cls, config, section='Syslog', **aux_opt_dict):
        '''Initialize log handler from sdg.config.Config object.'''

        opt_dict = config.validate_section \
                    (section, cls._opt_valid_dict, **aux_opt_dict)

        Syslog.init(**opt_dict)
