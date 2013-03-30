"""
UIUC Search filters
"""
import logging
import re
from spotseeker_server.org_filters.uiuc_ldap_client import get_res_street_address, get_edu_types
from spotseeker_server.models import SpotExtendedInfo
from spotseeker_server.org_filters import search

# UIUC LDAP
LOGGER = logging.getLogger(__name__)

# TODO: Add to settings...
UIUC_REQUIRE_ADDRESS = 'uiuc_require_address'
UIUC_REQUIRE_EDUTYPE = 'uiuc_require_edutype'

class Filter(search.Filter):
    keys = set((
        'eppn',
        ))

    def filter_results(self, spots):
        """
        Remove any spots the current user can't view, based:
            - resedential address matching the regex stored in the
                extended info
            - uiucEduType matching the value stored in the extended
                info
        """

        eppn = self.request.GET.get('eppn')
        if not eppn:
            LOGGER.info("User is not logged in. Show all spots.")
            result = spots
        else:
            # User logged in
            LOGGER.info("User is logged in. Show only spots they may access.")

            result = set()
            full_address = get_res_street_address(eppn)
            edutypes = get_edu_types(eppn)
            for spot in spots: 
                add_spot = True

                try:
                    restrict_rule = spot.spotextendedinfo_set.get(
                            key=UIUC_REQUIRE_ADDRESS)
                    regex_text = restrict_rule.value
                    if re.search(regex_text, full_address, re.I):
                        LOGGER.debug("Restricted, user address matches.")
                    else:
                        LOGGER.debug("Restricted, no address match.")
                        add_spot = False
                except SpotExtendedInfo.MultipleObjectsReturned:
                    LOGGER.error("Spot %s has multiple %s values" % (spot, UIUC_REQUIRE_ADDRESS))
                    add_spot = False
                except SpotExtendedInfo.DoesNotExist:
                    # This is not a restricted spot.
                    LOGGER.debug("No restricted.")

                try:
                    restrict_rule = spot.spotextendedinfo_set.get(
                        key=UIUC_REQUIRE_EDUTYPE)
                    edutype = restrict_rule.value
                    if edutype in edutypes:
                        LOGGER.debug("Restricted, user type matches.")
                    else:
                        LOGGER.debug("Restricted, no types match.")
                        add_spot = False
                except SpotExtendedInfo.MultipleObjectsReturned:
                    LOGGER.error("Spot %s has multiple %s values" % (spot, UIUC_REQUIRE_EDUTYPE))
                    add_spot = False
                except SpotExtendedInfo.DoesNotExist:
                    # This is not a restricted spot.
                    LOGGER.debug("No restricted.")

                if add_spot:
                    result.add(spot)

        return result

