"""
UIUC limiting to uiucEduTypes
"""
import logging
from spotseeker_server.org_filters.uiuc_ldap_client import get_edu_types
from spotseeker_server.models import SpotExtendedInfo
from spotseeker_server.org_filters import search

# UIUC LDAP
LOGGER = logging.getLogger(__name__)

# TODO: Add to settings...
# UIUC_REQUIRE_EDUTYPE = settings.UIUC_REQUIRE_EDUTYPE
UIUC_REQUIRE_EDUTYPE = 'uiuc_require_edutype'

class Filter(search.Filter):
    keys = set(['eppn'])

    def filter_results(self, spots):
        """
        Remove any spots that the current user can't use, based on
        their uiucEduType field and the value stored in the spot's
        extended info.
        """

        eppn = self.request.GET.get('org_filter:eppn')
        if not eppn:
            LOGGER.info("User is not logged in. Show all spots.")
            result = spots
        else:
            # User logged in
            LOGGER.info("User is logged in. Show only spots they may access.")

            result = set()
            edutypes = get_edu_types(eppn)
            for spot in spots: 
                try:
                    restrict_rule = spot.spotextendedinfo_set.get(
                        key=UIUC_REQUIRE_EDUTYPE)
                    edutype = restrict_rule.value
                    if edutype in edutypes:
                        LOGGER.debug("Restricted, user type matches.")
                        result.add(spot)
                    else:
                        LOGGER.debug("Restricted, no types match.")
                except SpotExtendedInfo.MultipleObjectsReturned:
                    LOGGER.error("Spot %s has multiple %s values" % (spot, UIUC_REQUIRE_EDUTYPE))
                except SpotExtendedInfo.DoesNotExist:
                    # This is not a restricted spot.
                    LOGGER.debug("No restricted.")
                    result.add(spot)
        return result

