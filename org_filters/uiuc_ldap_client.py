"""
University of Illinois/NCSA Open Source License

Copyright (c) 2013 Board of Trustees, University of Illinois
All rights reserved.

Developed by:       CITES Software Development Group
                    University of Illinois
                    http://cites.illinois.edu                            

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal with the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

	Redistributions of source code must retain the above copyright
	notice, this list of conditions and the following disclaimers.

	Neither the names of CITES Software Development Group,
	University of Illinois, nor the names of its contributors may
	be used to endorse or promote products derived from this
	Software without specific prior written permission. 

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR
ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH THE SOFTWARE. 
"""

# Python library imports
from string import Template
import ldap
import ldap.filter
from ldap.ldapobject import ReconnectLDAPObject
from django.conf import settings
from django.core.cache import cache
import logging
import re
from copy import deepcopy

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

def get_edu_types(eppn):
    '''Return the uiucEduType values as a set'''
    raw_data = get_person_ad_data(eppn)
    if raw_data is not None and 'uiucEduType' in raw_data:
        return set(raw_data['uiucEduType'])
    else:
        return set()

def get_res_street_address(eppn):
    '''Return the Residence Hall street address 
    for the student, if they have one.'''
    full_address = ''
    raw_data = get_person_ad_data(eppn)
    if len(raw_data) != 0:
        address_keys = [
                 'uiucEduResHallAddressLine1',
                 'uiucEduResHallAddressLine2',
                 'uiucEduResHallAddressLine3',
              ]
        for key in address_keys:
            full_address += raw_data.get(key, [''])[0]
    return full_address

def get_person_ad_data(eppn):
    '''
        Get needed LDAP information
    '''
	
    if eppn is None or len(eppn) <= 0 or len(eppn[0]) <= 0:
        # NetID does not actually exist - proceed no further!
        return None

    cache_key = "uiuc_ldap_client:get_person_ad_data:{0}".format(eppn)
    results = cache.get(cache_key)
    if results is not None:
        LOGGER.debug("Using cached search for %s", eppn)
        return results

    LOGGER.debug("Get AD connection.")
    ldap_conn = get_ldap_client()
    LOGGER.debug("AD connection: %s", str(ldap_conn))
	
    filter_template_string = '(eduPersonPrincipalName=$eppn)'
    return_attrs = [
            'uiucEduNetID',
            'uiucEduType',
            'uiucEduResHallAddressLine1',
            'uiucEduResHallAddressLine2',
            'uiucEduResHallAddressLine3',
            'uiucEduResHallAddressCity',
            'uiucEduResHallAddressStateCode',
            'uiucEduResHallAddressZipCode',
            ]

    filter_template = Template(filter_template_string)
    ldap_filter = filter_template.substitute({
        "eppn": ldap.filter.escape_filter_chars(eppn)
        })
    LOGGER.debug("Person filter is: %s", ldap_filter)

    ##Perform the query
    results = ldap_conn.lookup(ldap_filter, attr_list=return_attrs)
        
    if not results:
        LOGGER.warning("No return from get_person_ad_data")
        return None

    if len(results) > 1:
        LOGGER.warning("More than one ad_data for person search.")

    if len(results) <= 0:
        LOGGER.warning("No ad_data for person search.")
        return None
        
    results = results[0][1]
    
    for fieldname in results.keys():
        # Checkf for 0 length values and delete those
        if len(results[fieldname]) == 0:
            LOGGER.warn("%s returned with length zero from AD. It will not be available in the templates.", fieldname)
            del results[fieldname]

    if len(results) <= 0:
        LOGGER.debug("No AD return data.")
        return None

    LOGGER.debug("Returning AD data.")
    cache.set(cache_key, results)

    return results
	
