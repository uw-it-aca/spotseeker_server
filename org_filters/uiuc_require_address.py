"""
UIUC Residence Limits for Labs
"""
import logging
import re
from spotseeker_server.org_filters.uiuc_ldap_client import get_res_street_address
from spotseeker_server.models import SpotExtendedInfo

# UIUC LDAP
LOGGER = logging.getLogger(__name__)

# TODO: Add to settings...
# UIUC_REQUIRE_ADDRESS = settings.UIUC_REQUIRE_ADDRESS
UIUC_REQUIRE_ADDRESS = 'uiuc_require_address'

def filter_query(request, query):
    return (query, False)

def filter_results(request, spots):
    # Remove any spots that the current user cannot use (i.e. login, print, etc)

    eppn = request.GET.get('org_filter:eppn')
    if not eppn:
        LOGGER.info("User is not logged in. Show all spots.")
        result = spots
    else:
        # User logged in
        LOGGER.info("User is logged in. Show only spots they may access.")

        result = set()
        full_address = get_res_street_address(eppn)
        for spot in spots: 
            try:
                restrict_rule = spot.spotextendedinfo_set.get(
                    key=UIUC_REQUIRE_ADDRESS)
                regex_text = restrict_rule.value
                if re.search(regex_text, full_address):
                    LOGGER.debug("Restricted, user address matches.")
                    result.add(spot)
                else:
                    LOGGER.debug("Restricted, no address match.")
            except SpotExtendedInfo.MultipleObjectsReturned:
                LOGGER.error("Spot %s has multiple %s values" % (spot, UIUC_REQUIRE_ADDRESS))
            except SpotExtendedInfo.DoesNotExist:
                # This is not a restricted spot.
                LOGGER.debug("No restricted.")
                result.add(spot)
    return result

