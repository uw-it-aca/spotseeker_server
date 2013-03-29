'''
    Provides the search_ldap method
'''

# Python library imports
from string import Template
import ldap
from ldap.ldapobject import ReconnectLDAPObject
from django.conf import settings
import logging
import re

# SDG Standard Imports
from sdg.directory import (
    DirectoryConnection,
    ActiveDirectoryConnection,
    DirectoryResponseList,
    DirectoryResponseDict,
)

LOGGER = logging.getLogger(__name__)

# Global variables for the Classes
RETRY_DELAY = 1
RETRY_MAX = 4

class ScopeFixDirectoryConnection(DirectoryConnection):
    """
    Subclass to override lookup to accept the scope as an argument so this class
    can be used to work with doing user group correlations. 
    """
    def __init__(self, **opt_dict):
        super(ScopeFixDirectoryConnection, self).__init__(**opt_dict)
        self.uri = opt_dict['uri']
        self.bind_dn = opt_dict['bind_dn']

    def __str__(self):
        return "ScopeFixADConnection" + \
            " URI: %s" % self.uri + \
            " User: %s" % self.bind_dn + \
            " Search Base: %s" % self.base_dn + \
            " Default attrs: %s" % self.attr_list + \
            ""

    def lookup(self, ldap_filter, attr_list=None, base_dn=None, scope=None):
        '''Generic LDAP search method using standard LDAP filter string.'''

        #   If no attr_list supplied on method call, use attr_list from
        #   constructor.
        if attr_list is None:
            attr_list = self.attr_list

        #   If no base_dn supplied on method call, use base_dn from constructor.
        if base_dn is None:
            base_dn = self.base_dn

        #   No base_dn supplied on either method call or constructor.
        if base_dn is None:
            raise self.BaseDNMissingError('no base_dn specified')

        # If the scope is not provided, then use SCOPE_SUBTREE by default.
        if scope is None:
            scope = ldap.SCOPE_SUBTREE

        #   Perform LDAP search.
        result_list = self.connection.search_s(
                base_dn, scope, ldap_filter, attrlist=attr_list)

        #   Create DirectoryResponseList containing DirectoryResponseDict
        #   object for each entry returned from directory server.
        # If the DN is None it is a referral, so ignore it.
        return DirectoryResponseList(
                (dn, DirectoryResponseDict(attr_dict)) for \
                dn, attr_dict in result_list if dn is not None)

class SDGADConnectionPool(object):
    '''
        Creates one Active Directory SDG Directory connection for use multiple times.
    '''
    uri = settings.LDAP_INFO['url']
    bind_dn = settings.LDAP_INFO['user']
    password = settings.LDAP_INFO['password']
    person_ou = settings.LDAP_INFO['person_ou']

    dictionary = dict()
    dictionary = {
        'uri': uri,
        'retry_delay': RETRY_DELAY,
        'retry_max': RETRY_MAX,
        'base_dn': person_ou,
        'bind_dn': bind_dn,
        'password': password,
        }
    ldap.set_option(ldap.OPT_REFERRALS, 0)
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    conn = ScopeFixDirectoryConnection(**dictionary)
    LOGGER.debug('Created shared SDG LDAP connection: %s', str(conn))
    # Search Scope defaults to 'subtree', which works for our purposes.

def get_ldap_client():
    '''
        Returns an Active Directory client populated from settings
    '''

    return SDGADConnectionPool.conn

#---------------------------------------------------------------------------------------------------

def get_res_street_address(eppn):
    '''Return the Residence Hall street address 
    for the student, if they have one.'''
    full_address = ''
    raw_data = get_person_ad_data(eppn)
    if len(raw_data) != 0:
        address_keys =[
                 'uiucEduResHallAddressLine1',
                 'uiucEduResHallAddressLine2',
                 'uiucEduResHallAddressLine3',
              ]
        for key in address_keys:
            full_address += raw_data.get(key, '')
    return full_address

def get_person_ad_data(eppn):
    '''
        Get needed LDAP information
    '''
	
    if eppn is None or len(eppn) <= 0 or len(eppn[0]) <= 0:
        # NetID does not actually exist - proceed no further!
        return None

    LOGGER.debug("Get AD connection.")
    ldap_conn = get_ldap_client()
    LOGGER.debug("AD connection: %s", str(ldap_conn))
	
    filter_template_string = \
        '(eduPersonPrincipalName=$eppn)'
    return_attrs = \
            ['uiucEduNetID',
             'uiucEduResHallAddressLine1',
             'uiucEduResHallAddressLine2',
             'uiucEduResHallAddressLine3',
             'uiucEduResHallAddressCity',
             'uiucEduResHallAddressStateCode',
             'uiucEduResHallAddressZipCode',
            ]

    filter_template = Template(filter_template_string)
    ldap_filter = filter_template.substitute({"eppn":ldap.filter.escape_filter_chars(eppn)})
    LOGGER.debug("Person filter is: " + str(ldap_filter))

    ##Perform the query
    results = ldap_conn.lookup(ldap_filter,
        attr_list = return_attrs)
        
    if not results:
        LOGGER.warning("No return from get_person_ad_data")
        return None

    if len(results) > 1:
        LOGGER.warning("More than one ad_data for person search.")

    if len(results) <= 0:
        LOGGER.warning("No ad_data for person search.")
        return None
        
    results = results[0][1]
    return_data = {}
    
    for fieldname in results:
        # Grab the first value for the templates
        if len(results[fieldname]) > 0:
            return_data[fieldname] = results[fieldname][0]
            if fieldname == 'uiucEduNetID':
                LOGGER.debug("Fetched " + fieldname)
                LOGGER.debug("YES! ")
        else:
            error_msg = fieldname + " returned with length zero " +\
                "from AD. It will not be available in " + \
                " the templates."
            LOGGER.warn(error_msg)

        # Warn for any multivalue field.
        if len(results[fieldname]) > 1:
            error_msg = fieldname + " has multiple values in " +\
                    "the AD. Only the first value is " +\
                    "available in the page templates."
            LOGGER.warn(error_msg)

    if len(return_data) <= 0:
        LOGGER.debug("No AD return data.")
        return None

    LOGGER.debug("Returning AD data.")
         
    return return_data
	
