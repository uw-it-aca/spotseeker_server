"""
UIUC Residence Limits for Labs
"""
import logging
from spotseeker_server.org_filters.uiuc_ldap_client import get_res_street_address

# UIUC LDAP
LOGGER = logging.getLogger(__name__)

# TODO: Add to settings...
# UIUC_REQUIRE_ADDRESS = settings.UIUC_REQUIRE_ADDRESS
UIUC_REQUIRE_ADDRESS = 'uiuc_require_address'

class SearchFilter:
    def filter_query(request, query):
        return (query, False)

    def filter_results(request, spots):
        # Remove any spots that the current user cannot use (i.e. login, print, etc)

        email = request.GET.get('org_filter:email_address')
        if not email:
            LOGGER.info("User is not logged in. Show all spots.")
            result = spots
        else:
            # User logged in
            LOGGER.info("User is logged in. Show only spots they may access.")

            result = set()
            full_address = get_res_street_address(email)
            for spot in spots: 
                address_restrictions = spot.spotextendedinfo_set.get(
                        key=UIUC_REQUIRE_ADDRESS)
                # This is not a restricted spot.
                if len(address_restrictions) == 0:
                    LOGGER.debug("Not restricted.")
                    result.add(spot)
                else:
                    # Assume only one uiuc restriction per spot.
                    restrict_rule = address_restrictions[0]
                    regex_text = restrict_rule.value
                    if re.match(regex_text, full_address):
                        LOGGER.debug("Restricted, user address matches.")
                        result.add(spot)
                    else:
                        LOGGER.debug("Restricted, no address match.")

        return result

