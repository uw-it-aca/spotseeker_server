#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/directory.py $
#   $Revision: 33324 $ $Date: 2012-12-17 12:24:23 -0600 (Mon, 17 Dec 2012) $

#   Copyright (c) 2011, 2012 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''
Directory utility class for CITES Software Development Group applications.
'''

from __future__ import absolute_import

import ldap
import logging
import warnings

from sdg import log

#   Default object class for LDAP connection.
LDAP_OBJECT_CLASS   = ldap.ldapobject.ReconnectLDAPObject

#   Initialize module logger.
LOGGER = log.init_module_logger()

#####

class DirectoryConnection(object):
    '''
    Superclass for various types of directory connections. Applications 
    ordinarily do not instantiate this class directory. Applications should
    instead instantiate an appropriate subclass of DirectoryConnection.
    '''

    class BaseDNMissingError(Exception):
        '''
        Exception raised when base DN is not supplied in either
        constructor or method call.
        '''
        pass

    class NotFoundError(Exception):
        '''
        Exception raised when LDAP search expecting single result yielded
        no results.
        '''
        pass

    class TooManyError(Exception):
        '''
        Exception raised when LDAP search expecting single result yielded
        more than one result.
        '''
        pass

    #   Dictionary of configuration keywords and whether they are required.
    _opt_valid_dict = \
        {
        'base_dn'       : False,
        'bind_dn'       : False,
        'password'      : False,
        'retry_delay'   : False,
        'retry_max'     : False,
        'uri'           : True,
        'user'          : False,        ##### TODO deprecate in future
        }

    #####

    def __init__(self, **opt_dict):
        '''Initialize directory connection.'''

        #   Validate that required options are present. 
        #   FIXME needs improvement; report *all* missing options!
        #   pylint: disable=C0103
        for kw, required in self._get_valid_option_dict().items():
            if not required:
                continue

            if kw not in opt_dict or not opt_dict[kw]:
                raise Exception \
                        ('required option \'%s\' missing or invalid' % kw)

        #   pylint: disable=W0613,W0622,R0913
        def log_warning(message, category, filename, lineno, 
                        file=None, line=None):
            '''Send PendingDeprecationWarning to logger instead of stderr.'''
            logging.warning('%s:%s: %s:%s', filename, lineno, 
                            category.__name__, message)
            return

        #   Initialize attribute list.
        self.attr_list = []

        #   Initialise base DN.
        self.base_dn    = None

        ##### FIXME Begin temporary warning code.
        if not 'bind_dn' in opt_dict and 'user' in opt_dict:
            opt_dict['bind_dn'] = opt_dict['user']
            with warnings.catch_warnings():
                warnings.simplefilter('always')

                showwarning_orig = warnings.showwarning
                warnings.showwarning = log_warning

                warnings.warn \
                    (('use of option \'user\' by %s is deprecated; ' +
                      'use \'bind_dn\' instead') % self.__class__.__name__,
                     PendingDeprecationWarning,
                     stacklevel=2)
                warnings.showwarning = showwarning_orig
        ##### FIXME End temporary warning code.

        #   Replace default attribute list with list from caller.
        if 'attr_list' in opt_dict:
            self.attr_list = opt_dict['attr_list']

        if 'base_dn' in opt_dict:
            self.base_dn   = opt_dict['base_dn']

        LOGGER.debug('trying %s', opt_dict['uri'])

        #   Initialize directory connection. The kw_args dict is used to
        #   support keywords whose validity depends on which LDAP object
        #   class is being constructed.
        ldap_kw_args = dict()

        #   If we're using the ReconnectLDAPObject class, see if configuration
        #   includes options pertinent to that module; if so, update them
        #   into kw_args.
        if issubclass(LDAP_OBJECT_CLASS, ldap.ldapobject.ReconnectLDAPObject):
            if 'retry_delay' in opt_dict:
                ldap_kw_args.update(dict(retry_delay=opt_dict['retry_delay']))
            if 'retry_max' in opt_dict:
                ldap_kw_args.update(dict(retry_max=opt_dict['retry_max']))

        #   Initialize LDAP connection.
        self.connection = LDAP_OBJECT_CLASS(opt_dict['uri'], **ldap_kw_args)
        LOGGER.debug('connected to %s', opt_dict['uri'])

        #   If credentials are specified, bind to them.
        if 'bind_dn' in opt_dict and 'password' in opt_dict:
            LOGGER.debug('binding as %s', opt_dict['bind_dn'])
            self.connection.simple_bind_s \
                (opt_dict['bind_dn'], opt_dict['password'])

        else:
            #   Not using bound connection.
            LOGGER.debug('using unbound connection')

        return

    #####

    @classmethod
    def _get_valid_option_dict(cls):
        '''
        Return dictionary of valid options for DirectoryConnection. Used
        by factory functions ActiveDirectoryConnectionFromConfig and
        CentralRegistryConnectionFromConfig to spsecify permitted keyword
        arguments. Also specifies which of those arguments are mandatory.
        '''
        return cls._opt_valid_dict

    #####

    #   pylint: disable=W0622
    def lookup(self, ldap_filter, attr_list=None, base_dn=None):
        '''Generic LDAP search method using standard LDAP filter string.'''

        #   If no attr_list supplied on method call, use attr_list from
        #   constructor.
        if not attr_list:
            attr_list = self.attr_list

        #   If no base_dn supplied on method call, use base_dn from constructor.
        if not base_dn:
            base_dn = self.base_dn

        #   No base_dn supplied on either method call or constructor.
        if not base_dn:
            raise DirectoryConnection.BaseDNMissingError('no base_dn specified')

        #   Perform LDAP search.
        result_list = self.connection.search_s \
                        (base_dn, ldap.SCOPE_SUBTREE, ldap_filter,
                         attrlist=attr_list)

        #   Create DirectoryResponseList containing DirectoryResponseDict
        #   object for each entry returned from directory server.
        return DirectoryResponseList \
                ((dn, DirectoryResponseDict(attr_dict))
                    for dn, attr_dict in result_list)

    #####

    #   pylint: disable=W0622
    def lookup_single(self, ldap_filter, attr_list=None, base_dn=None,
                      return_dn=False):
        '''
        LDAP search method using standard LDAP filter string. Expects 
        exactly one result and raises NotFoundError or TooManyError if
        this is not true. Returns DirectoryResponseDict on success.
        '''

        #   Perform LDAP search.
        result_list = self.lookup(ldap_filter,
                                  attr_list=attr_list, base_dn=base_dn)

        #   Raises exception unless result_list contains exactly one entry.
        if len(result_list) == 0:
            raise self.NotFoundError \
                ('no results for search with filter \'%s\'' % ldap_filter)

        if len(result_list) > 1:
            raise self.TooManyError \
                ('too many results (%d) for search with filter \'%s\'' %
                    (len(result_list), ldap_filter), len(result_list))

        #   Return single DirectoryResponseDict object from search; dn is
        #   not used.
        #   pylint: disable=C0103
        dn, directory_entry = result_list[0]
        
        #   If dn requested, return it and directory entry
        if return_dn:
            return dn, directory_entry

        #   Otherwise just return directory entry.
        return directory_entry

#####

#   pylint: disable=C0103
class ActiveDirectoryConnection(DirectoryConnection):
    '''Class for retrieving data from the CITES Active Directory server.'''

    #####

    def lookup_by_netid(self, netid):
        '''Look up Active Directory entry by netid.'''

        return self.lookup(ldap_filter='cn=' + netid)

#####

#   pylint: disable=C0103
def ActiveDirectoryConnectionFromConfig(config, **opt_dict):
    '''
    Factory method for returning ActiveDirectory connection specified in a
    configuration file; the config argument must be a sdg.config.Config object.
    '''

    #   pylint: disable=W0212
    opt_dict = config.validate_section \
                ('ActiveDirectory', 
                 DirectoryConnection._get_valid_option_dict(), **opt_dict)

    ldap.set_option(ldap.OPT_REFERRALS, 0)
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

    return ActiveDirectoryConnection(**opt_dict)

#####
    
class CampusLDAPConnection(DirectoryConnection):
    '''Class for retrieving data from the CITES Campus LDAP server.'''
    
    #####

    def lookup_by_netid(self, netid):
        '''Look up Campus LDAP entry by netid.'''

        return self.lookup(ldap_filter='uiucEduNetID=' + netid)

    #####

    def lookup_by_registry_unique_id(self, unique_id):
        '''Look up Central Registry entry by registry unique ID.'''

        return self.lookup(ldap_filter='uiucEduRegistryUniqueID=' + unique_id)

    #####

    def lookup_by_uin(self, uin):
        '''Look up Central Registry entry by UIN.'''

        return self.lookup(ldap_filter='uiucEduUIN=' + uin)

#####

def CampusLDAPConnectionFromConfig(config, **opt_dict):
    '''
    Factory method for returning Campus LDAP connection specified in a
    configuration file; the config argument must be a sdg.config.Config object.
    '''

    #   pylint: disable=W0212
    opt_dict = config.validate_section \
                ('CampusLDAP', DirectoryConnection._get_valid_option_dict(),
                 **opt_dict)

    ldap.set_option(ldap.OPT_REFERRALS, 1)
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_TRY)

    return CampusLDAPConnection(**opt_dict)

#####

class DirectoryResponseDict(dict):
    '''
    Subclass that extends dict class to provide additional methods
    pertinent to retrieving values from the dict objects returned by the
    ldap module.
    '''
    
    #####

    def get_multivalue(self, attr_name):
        '''Return values of specified attribute as list.'''

        #   Return attribute as list.
        return self[attr_name]

    #####

    def get_single(self, attr_name):
        '''Return single value from attribute.'''

        #   Raise ValueError on attempt to fetch single value from multi-
        #   valued attribute.
        if len(self[attr_name]) > 1:
            raise ValueError('LDAP attribute %s has >1 value' % attr_name)

        #   Return first (and only) member of list.
        return self[attr_name][0]
#####

class DirectoryResponseList(list):
    '''
    Subclass that extends list class to provide additional methods
    pertinent to retrieving results from a directory server.
    '''

    pass
