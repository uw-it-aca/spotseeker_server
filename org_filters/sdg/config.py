#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/config.py $
#   $Revision: 32490 $ $Date: 2012-10-10 12:05:38 -0500 (Wed, 10 Oct 2012) $

#   Copyright (c) 2011-2012 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''Conifiguration processing class.'''

import datetime
import cStringIO
import ipaddr
import logging
import operator
import os
import sys
import types
import warnings

from ConfigParser import NoSectionError, SafeConfigParser

from sdg.attrdict import AttrDict
from sdg import log

#   Initialize module logger.
LOGGER = log.init_module_logger()

#_re_python_attr = re.compile('[a-z_][a-z0-9_]')

#####

def _validate_validator(validator):
    '''Validate that validator callback argument is proper type.'''

    if isinstance(validator, types.FunctionType):
        return

    raise TypeError('validator callback must be %s; got %s' % 
                    (str(types.FunctionType), str(validator)))

#####

class ConfigError(Exception):
    '''
    Exception raised by Config.validate() and Section.validate()
    when errors are encountered during validation.  Contains a
    list of individual exceptions.
    '''

    #####

    def all(self):
        '''Return all errors from exception object's internal list.'''
        return self.args

    #####

    def format_error(self):
        '''
        Format configuration errors, one line per error. Returns result string.
        '''
        text = None
        for error in self.all():
            if text is None:
                text = str(error)
            else:
                text += '\n' + str(error)
        return text

    #####

    def log_error(self, level=logging.ERROR):
        '''Log configuration errors, using one log entry per error.'''
        for error in self.all():
            logging.log(level, str(error))
        return

    #####

    def print_error(self, stream=sys.stderr):
        '''
        Print to specified stream a formatted multi-line string describing
        configuration errors.
        '''
        print >> stream, self.format_error()
        return

#####

class Config(object):
    '''Configuration file management.'''

    #####

    class ConfigurationNotFoundError(Exception):
        '''Exception raised when configuration file couldn't be found.'''
        pass

    #####

    class ConflictingOptionError(Exception):
        '''
        Exception raised when option appears both in option file and
        parameter list. (To be deprecated; do not use for new applications.)
        '''
        pass

    #####

    class MissingOptionError(Exception):
        '''
        Exception raised when required configuration option is missing.
        (To be deprecated; do not use for new applications.)
        '''
        pass

    #####

    class UnknownOptionError(Exception):
        '''
        Exception raised when unknown configuration option encountered.
        (To be deprecated; do not use for new applications.)
        '''
        pass

    #####

    class ValidationError(Exception):
        '''
        Exception raised by validator methods when option or section
        validator callback fails. Specially handled by Config.validate()
        and Section.validate().
        '''
        pass

    #   Verbosity level for class.
    verbose     = 0

    #####

    def __getattr__(self, attr):
        '''Allow Config's section dictionary to be accessed as attribute.'''
        return self._section_dict[attr.lower()]

    #####

    def __init__(self, config):
        '''New Config, used to describe a configuration file. '''

        self._section_dict  = dict()

        #####

        #   pylint: disable=W0613,W0622,R0913
        def log_warning(message, category, filename, lineno, 
                        file=None, line=None):
            '''Send PendingDeprecationWarning to logger instead of stderr.'''
            logging.warning('%s:%s: %s:%s', filename, lineno, 
                            category.__name__, message)
            return

        #   If instance is a Config object rather than a subclass of Config,
        #   issue PendingDeprecationWarning.
        if type(self) == Config:
            with warnings.catch_warnings():
                warnings.simplefilter('always')

                showwarning_orig = warnings.showwarning
                warnings.showwarning = log_warning

                warnings.warn \
                    ('use of Config as base class is deprecated; ' +
                     'use ConfigFile instead', PendingDeprecationWarning,
                     stacklevel=2)
                warnings.showwarning = showwarning_orig

        #   Initialize parser.
        self.parser = SafeConfigParser()

        #   If config is a string, assume it's a filename. Determine if
        #   it exists and then try to read it.
        if isinstance(config, types.StringTypes):
            if not os.path.exists(config):
                raise Config.ConfigurationNotFoundError \
                        ('configuration file \'%s\' not found' % 
                         os.path.abspath(config))
                
            else:
                #   pylint: disable=E1101
                logging.debug('opening config file %s', config)

            self.parser.read(config)

        #   If config is a file-like object; seek to beginning and read it.
        elif isinstance(config, (cStringIO.OutputType, types.FileType)):
            config.seek(0)
            self.parser.readfp(config)

        else:
            raise TypeError('invalid object type: %s' % \
                            config.__class__.__name__)

        return

    #####

    def validate_section(self, section, valid_opt_dict, 
                         ignore_missing_section=False, ignore_unknown=True,
                         **aux_opt_dict):
        '''
        Validates section and returns dictionary of configuration values
        from that section. (Used by legacy code.)
        '''

        #   List of keys in desired section.
        section_opt_list    = []

        #   Dictionary used to build option list combined from config
        #   options and keyword arguments..
        opt_dict            = {}

        #   Lists of error cases.
        opt_conflict_list   = []
        opt_missing_list    = []
        opt_unknown_list    = []

        #   Retrieve list of options from requested config section.
        try:
            section_opt_list = self.parser.options(section)

        except NoSectionError:
            if not ignore_missing_section:
                raise

        else:
            #   No exception raised; retrieve option values from config section.
            for opt in section_opt_list:
                #   Check whether we have a conflict.
                if opt in aux_opt_dict:
                    opt_conflict_list.append(opt)
                else:
                    opt_dict[opt] = self.parser.get(section, opt)

        #   One or more options appear in both config file and aux_opt_dict.
        if len(opt_conflict_list):
            raise self.ConflictingOptionError \
                ('option(s) appear more than once: %s' % 
                 ', '.join(opt_conflict_list))

        #   Update opt_dict with contents of aux_opt_dict.
        opt_dict.update(aux_opt_dict)

        #   Check whether option is required.
        for opt, required in valid_opt_dict.items():
            #   Ignore non-required option.
            if not required:
                continue

            #   Add option to missing list.
            if not opt in opt_dict:
                opt_missing_list.append(opt)

        #   One or more options are missing.
        if len(opt_missing_list):
            raise self.MissingOptionError \
                ('required option(s) are missing: %s' % 
                 ', '.join(opt_missing_list))

        #   Handle unknown options.
        for opt in opt_dict.keys():
            #   Add option to unexpected list.
            if not opt in valid_opt_dict.keys():
                opt_unknown_list.append(opt)

        #   Return if ignoring unknown options.
        if ignore_unknown:
            return opt_dict

        #   One or more unknown options were encountered.
        if len(opt_unknown_list):
            raise self.UnknownOptionError \
                ('unknown option(s) encountered: %s' % 
                 ', '.join(opt_unknown_list))

        return opt_dict

    #####

    def add_section(self, name, default_dict=None, validate=None):
        '''Add a Section belonging to this configuration.'''

        if hasattr(self, name.lower()):
            raise ValueError('section \'%s\' already exists' % name)

        config_section = Section(self.parser, name, \
                                 default_dict=default_dict, validate=validate)
        self._section_dict[name.lower()] = config_section
        return config_section

    #####

    def get_section(self, section_name):
        '''Returns section by name.'''
        return self.__getattr__(section_name)

    #####

    def sections(self):
        '''Returns list of sections in this configuration.'''
        return sorted(self._section_dict.keys())

    #####

    def validate(self):
        '''Validate all sections in this configuration.'''
        #   pylint: disable=W0141
        map(Section.validate, 
            [ getattr(self, x) for x in self.sections() ])
        return

#####

class ConfigFile(Config):
    '''Configuration file management.'''

    pass

#####

class OptionTypeConverter(object):
    '''Type converters used internally.'''
    
    #   Default format for date validation.
    FMT_DATE            = '%Y/%m/%d'
    
    FMT_DATETIME        = '%Y/%m/%d %H:%M:%S'
    
    FMT_TIME            = '%H:%M:%S'

    _boolean_states = \
         {
         '1': True,  'yes': True,  'true':  True,  'on':  True,
         '0': False, 'no':  False, 'false': False, 'off': False,
         }

    #####

    @staticmethod
    def _bool(value):
        '''
        Converts string value to a boolean, considering typical values
        like true, no, false, 1.
        '''
        if value.lower() not in OptionTypeConverter._boolean_states:
            raise ValueError('Not a boolean: %s' % value)

        return OptionTypeConverter._boolean_states[value.lower()]

    #####

    @staticmethod
    def date(fmt=FMT_DATE):
        '''
        Converts string value to a date object, optionally using a 
        user-specified format.
        '''
        func = lambda(value) : datetime.datetime.strptime(value, fmt).date()

        #   Set name of lambda function to allow better debugging messages.
        func.func_name = 'date(\'%s\')' % fmt
        return func

    #####

    @staticmethod
    def datetime(fmt=FMT_DATETIME):
        '''
        Converts string value to a datetime object, optionally using a
        user-specified format.
        '''
        func = lambda(value) : datetime.datetime.strptime(value, fmt)
        func.func_name = 'datetime(\'%s\')' % fmt
        return func

    #####

    @staticmethod
    def int(base=10):
        '''
        Convert string value to an integer in specified base, which
        defaults to 10.
        '''
        func = lambda(value) : int(value, base)

        #   Set name of lambda function to allow better debugging messages.
        func.func_name = 'int(%d)' % base if base != 10 else 'int()'
        return func

    #####

    @staticmethod
    def _ip_address_helper(cls, **kw_arg_dict):
        func = lambda(value) : cls(value, **kw_arg_dict)

        version = kw_arg_dict.get('version', None)
        func.func_name = cls.__name__
        if version:
            func.func_name += '(version=%d)' % version
        return func

    #####

    @staticmethod
    def _ip_network_helper(cls, **kw_arg_dict):
        func = lambda(value) : cls(value, **kw_arg_dict)

        strict  = kw_arg_dict.get('strict',  None)
        version = kw_arg_dict.get('version', None)
        func.func_name = cls.__name__
        if version or strict:
            func.func_name += '('
            func.func_name += ('version=%d' % version) if version else ''
            if version and strict:
                func.func_name += ', '
            if strict:
                func.func_name += 'strict'
            func.func_name += ')'

        return func

    #####

    @staticmethod
    def ip_address(version=None):
        return OptionTypeConverter._ip_address_helper \
                    (ipaddr.IPAddress, version=version)

    #####

    @staticmethod
    def ip_network(version=None, strict=False):
        return OptionTypeConverter._ip_network_helper \
                    (ipaddr.IPNetwork, version=version, strict=strict)

    #####

    @staticmethod
    def ipv4_address():
        return OptionTypeConverter._ip_address_helper(ipaddr.IPv4Address)

    #####

    @staticmethod
    def ipv6_address():
        return OptionTypeConverter._ip_address_helper(ipaddr.IPv6Address)

    #####

    @staticmethod
    def ipv4_network(strict=False):
        return OptionTypeConverter._ip_network_helper \
                    (ipaddr.IPv4Network, strict=strict)

    #####

    @staticmethod
    def ipv6_network(strict=False):
        return OptionTypeConverter._ip_network_helper \
                    (ipaddr.IPv6Network, strict=strict)

    #####

    @staticmethod
    def time(fmt=FMT_TIME):
        '''
        Converts string value to a time object, optionally using a
        user-specified format.
        '''
        func = lambda(value) :  datetime.datetime.strptime(value, fmt).time()
        func.func_name = 'time(\'%s\')' % fmt
        return func

#####

class OptionRule(object):
    '''
    New OptionRule, used to describe an option and its
    validation rules.
    '''

    #   Dictionary containing types for which conversion is accepted along
    #   with their converter functions. Types with a None value are converted
    #   using the type's constructor method.
    _convert_dict = \
        {
        #   pylint: disable=W0212
        ipaddr.IPAddress    : OptionTypeConverter.ip_address(),
        ipaddr.IPNetwork    : OptionTypeConverter.ip_network(),
        types.BooleanType   : OptionTypeConverter._bool,
        types.FloatType     : None,
        types.IntType       : OptionTypeConverter.int(),
        types.LongType      : None,
        datetime.date       : OptionTypeConverter.date(),
        datetime.datetime   : OptionTypeConverter.datetime(),
        datetime.time       : OptionTypeConverter.time(),
        }

    _convert_dict_types = \
        tuple(x for x in _convert_dict.keys() if isinstance(x, types.TypeType))

    #####

    #   pylint: disable=W0622
    def __init__(self, option, type=None, validate=None):
        '''
        New OptionRule, used to specify a configuration
        option, required type, and validator callback.
        '''

        if validate is not None:
            _validate_validator(validate)

        if type is not None:
            self._validate_type(type)

        self._validator = validate
        self._option    = option
        self._type      = type
        return

    #####

    @property
    def validator(self):
        '''Validator function reference.'''
        return self._validator

    #####

    @property
    def option(self):
        '''Name of option.'''
        return self._option

    #####

    @property
    def type(self):
        '''Type to which option is converted.'''
        return self._type

    #####

    def convert(self, value):
        '''Convert value per rule's type converter.'''

        #   Retrieve converter for this type.
        converter = self._convert_dict.get(self.type)

        #   If converter is None, convert using type's constructor.
        if not converter:
            converter = self.type

        return converter(value)

    #####

    def __str__(self):
        if self.validator is not None:
            validator_name = self.validator.__name__
        else:
            validator_name = ''
        
        if self.type:
            type_name = self.type.__name__
        else:
            type_name = ''
        
        return '%s [%s:%s]' % (self.option, type_name, validator_name)

    #####

    @staticmethod
    def _validate_type(otype):
        '''Validate that option type is a member of the proper classes.'''

        #   If value is a type, validate it against type list.
        if isinstance(otype, types.TypeType):
            if issubclass(otype, OptionRule._convert_dict_types):
                return

        #   A value may be a function.
        elif isinstance(otype, types.FunctionType):
            return

        raise TypeError('improper type specification %s' % str(otype))

#####

class OptionValidator(object):
    '''Validators for ConfigOption values.'''
        
    #####

    @classmethod
    def choice(cls, choice_list):
        '''
        Returns function used to validate option as being in list of choices.
        '''
        func = lambda(option_dict) : \
                cls._validate_choices(option_dict, choice_list)
        func.func_name = 'choice(%s)' % ', '.join(sorted(str(choice) 
                                                for choice in choice_list))
        return func

    #####

    #   pylint: disable=C0103
    @classmethod
    def eq(cls, value):
        '''Returns function to validate equality to specified value.'''
        func = lambda(option_dict) : \
                cls._validate_opr(option_dict, operator.eq, value)
        func.func_name = 'eq(%s)' % value
        return func

    #####

    #   pylint: disable=C0103
    @classmethod
    def ge(cls, value):
        '''
        Returns function to validate greater than or equal to specified value.
        '''
        func = lambda(option_dict) : \
                cls._validate_opr(option_dict, operator.ge, value)
        func.func_name = 'ge(%s)' % value
        return func

    #####

    #   pylint: disable=C0103
    @classmethod
    def lt(cls, value):
        '''Returns function to validate less than specified value.'''
        func = lambda(option_dict) : \
                cls._validate_opr(option_dict, operator.lt, value)
        func.func_name = 'lt(%s)' % value
        return func

    #####

    #   pylint: disable=C0103
    @classmethod
    def le(cls, value):
        '''
        Returns function to validate less than or equal to specified value.
        '''
        func = lambda(option_dict) : \
                cls._validate_opr(option_dict, operator.le, value)
        func.func_name = 'le(%s)' % value
        func.func_name = '<= %s' % value
        return func

    #####

    #   pylint: disable=C0103
    @classmethod
    def gt(cls, value):
        '''Returns function to validate greater than specified value.'''
        func = lambda(option_dict) : \
                cls._validate_opr(option_dict, operator.gt, value)
        func.func_name = 'gt(%s)' % value
        return func

    #####

    #   pylint: disable=C0103
    @classmethod
    def ne(cls, value):
        '''Returns function to validate inequality to specified value.'''
        func = lambda(option_dict) : \
                cls._validate_opr(option_dict, operator.ne, value)
        func.func_name = 'ne(%s)' % value
        return func

    #####

    @classmethod
    def range(cls, low, high):
        '''Returns function used to validate option as being within range.'''
        func = lambda(option_dict) : \
                cls._validate_range(option_dict, low, high)
        func.func_name = 'range(%s, %s)' % (low, high)
        return func

    #####

    @staticmethod
    def _validate_choices(option_dict, choice_list):
        '''Validate that option values are from among specified choices.'''

        #   Iterate over multiple option/value pairs, which may be overkill.
        #   pylint: disable=W0612
        for option, value in sorted(option_dict.items()):
            if value not in choice_list:
                raise Config.ValidationError \
                        ('value %s fails: must be member of: %s' %
                         (value, ', '.join(sorted(str(choice) 
                            for choice in choice_list))))
        return

    #####

    @staticmethod
    def _validate_opr(option_dict, opr, target_value):
        '''
        Validate comparison operations (e.g., greater than or equal, less than,
        not equal) between the option values in dictionary and a target value.
        '''
        opr_string = dict(eq='==', ge='>=', gt='>', le='<=', lt='<', ne='!=')

        #   Iterate over multiple option/value pairs, which may be overkill.
        #   pylint: disable=W0612
        for option, value in sorted(option_dict.items()):
            if not opr(value, target_value):
                raise Config.ValidationError \
                        ('value %s fails: must be %s %s' %
                         (value, opr_string[opr.__name__], target_value))

        return
    #####

    @staticmethod
    def _validate_range(option_dict, low, high):
        '''
        Validate that option values in dictionary are in range 
        low <= option <= high.

        '''
        #   Iterate over multiple option/value pairs, which may be overkill.
        #   pylint: disable=W0612
        for option, value in sorted(option_dict.items()):
            if value < low or value > high:
                raise Config.ValidationError \
                        ('not in range: %s <= %s <= %s' % (low, option, high))

        return

#####

class Section(object):
    '''Representation of a configuration section.'''

    _msg_prefix_all     = 'configuration validation error:'
    _msg_prefix_section = ' '.join((_msg_prefix_all,        'section \'%s\':'))
    _msg_prefix_option  = ' '.join((_msg_prefix_section,    'option \'%s\':'))

    def _make_option_exception(self, rule, msg):
        '''Format and return an exception for an option validation error.'''
        msg = (self._msg_prefix_option + ' %s') % (self.name, rule.option, msg)
        return Config.ValidationError(msg)

    def _make_section_exception(self, msg):
        '''Format and return an exception for an section validation error.'''
        msg = (self._msg_prefix_section + ' %s') % (self.name, msg)
        return Config.ValidationError(msg)
        
    #####

    def __init__(self, parser, name, validate=None, default_dict=None):
        '''
        New Section, used to describe options and validation
        rules for a configuration section.
        '''

        #   Validate validator callback if specified.
        if validate:
            _validate_validator(validate)

        #   Populate private attributes from call.
        self._name          = name
        self._rule_list     = list()
        self._validator     = validate

        #   Populate _value_dict from default dictionary, updating with
        #   data parsed from this configuration section.
        self._value_dict = AttrDict()
        if default_dict:
            self._value_dict.update(default_dict.items())
        self._value_dict.update(parser.items(name))
        return

    #####

    def __getattr__(self, attr):
        '''Allow Section's value dictionary to be accessed as attribute.'''
        return self._value_dict[attr.lower()]

    #####

    def __str__(self):
        return  '%s:%x' % (self._name, id(self))

    #####

    def add_rule(self, rule):
        '''
        Add OptionRule to this section. Returns section object so
        that multiple invocations of this method call can be chained.
        '''

        #   Validate that rule is subclass of expected type.
        if not isinstance(rule, OptionRule):
            raise TypeError('wrong type object %s' % str(rule))

        #   Append rule to internal rule list.
        self._rule_list.append(rule)
        return self

    #####

    def get_option(self, option_name):
        '''Returns option by name.'''
        return self.__getattr__(option_name)

    #####

    @property
    def name(self):
        '''Name of section.'''
        return self._name

    #####

    def options(self):
        '''Returns list of configuration options found for this section.'''
        return sorted(self._value_dict.keys())

    #####

    def rules(self):
        '''Returns list of option rules defined for this section.'''
        return sorted(self._rule_list, key=lambda x : x.option)

    #####

    def validate(self):
        '''Validate configuration section.'''

        #   List for errors accumulated by validation.
        error_list  = list()

        #   pylint: disable=E1101
        logging.debug('validating section \'%s\'', self.name)

        temp_value_dict = dict()

        #   Iterate over all defined rules.
        for rule in self._rule_list:
            #   pylint: disable=E1101
            logging.debug('validating option \'%s\'', rule.option)

            #   Does section have this attribute?
            if not hasattr(self, rule.option):
                #   Append error to error list if option doesn't appear in
                #   options for section; skip further processing of this rule.
                logging.debug('option \'%s\' missing', rule.option)
                error_list.append(self._make_option_exception(rule, 
                                  'required option missing'))
                continue

            #   If valid rule type specified, perform type conversion.
            if rule.type:
                try:
                    value = self._convert_type(rule)
                    temp_value_dict[rule.option.lower()] = value

                except Config.ValidationError as exc:
                    error_list.append(exc)

                #   pylint: disable=W0703
                except Exception as exc:
                    #   Append any error produced by type conversion to
                    #   error list.
                    log.log_exception()
                    error_list.append \
                        (self._make_option_exception(rule, 
                                                     'EXCEPTION: %s' % exc))

                    #   pylint: disable=E1101
                    logging.debug \
                        ('option \'%s\' failed to convert to %s', 
                         rule.option, rule.type.__name__)
                    continue

                #   pylint: disable=E1101
                logging.debug \
                    ('option \'%s\' converted to %s', 
                     rule.option, rule.type.__name__)

            else:
                #   No type converstion necessary for string option.
                value = getattr(self, rule.option)

            #   If rule validator callback is specified, call it with
            #   AttrDict consisting of a single rule/value pair.
            if rule.validator:
                try:
                    #   Call rule validator callback with converted value.
                    self._run_rule_validator(rule, value)
    
                except Config.ValidationError as exc:
                    error_list.append(exc)
                    logging.debug('option \'%s\' failed to validate', 
                                        rule.option)

                except Exception as exc:
                    #   Log exception.
                    log.log_exception()
                    #   Append error produced by rule validator to error list.
                    error_list.append(exc)
                    logging.debug('option \'%s\' failed to validate', 
                                        rule.option)
                    continue

                logging.debug('option \'%s\' validated', rule.option)

        #   If section validator callback is specified, call it with
        #   AttrDict consisting of a single rule/value pair.
        if self.validator:
            try:
                self._run_section_validator()

            except Config.ValidationError as exc:
                error_list.append(exc)

            except Exception as exc:
                #   Log exception.
                log.log_exception()
                #   Append error produced by validator callback to error list.
                error_list.append(exc)

            else:
                logging.debug('section \'%s\' failed to validate', self)


        #   Process errors produced by any validation steps.
        if error_list:
            raise ConfigError(*error_list)

        self._value_dict.update(temp_value_dict)
        return

    #####

    @property
    def validator(self):
        '''Validator function reference.'''
        return self._validator

    #####

    def _convert_type(self, rule):
        '''Perform requested type conversion on specified rule.'''

        try:
            #   Retrieve attribute value and perform type conversion.
            value = rule.convert(getattr(self, rule.option))

        except ValueError:
            raise self._make_option_exception \
                    (rule, 'type conversion to %s failed' % rule.type.__name__)

        #   Method completed without error; return converted value.
        return value

    #####

    def _run_rule_validator(self, rule, value):
        '''Run validator callback on specified rule.'''

        #   pylint: disable=E1101
        logging.debug('running rule validator %s for option \'%s\'', 
                      rule.validator.__name__, rule.option)

        try:
            rule.validator(AttrDict({ rule.option : value }))

        except Config.ValidationError as exc:
            raise self._make_option_exception(rule, exc)
            
        #   Method completed without error.
        return

    #####

    def _run_section_validator(self):
        '''Run validator callback on Section.'''

        #   pylint: disable=E1101
        logging.debug('running section validator %s', 
                      self._validator.__name__)

        try:
            self.validator(self)

        except Config.ValidationError as exc:
            raise self._make_section_exception(exc)

        #   Method completed without error.
        return
