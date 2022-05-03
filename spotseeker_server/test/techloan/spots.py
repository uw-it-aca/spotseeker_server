# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import override_settings
from django.conf import settings
from spotseeker_server.spotseeker_server.management.commands.\
    techloan.spotseeker import Spots
from spotseeker_server.spotseeker_server.test.techloan import TechloanTestCase


@override_settings(SPOTSEEKER_TECHLOAN_URL="")
class SpotseekerServerTest(TechloanTestCase):

    # mock SPOTSEEKER_TECHLOAN_UPDATER envvar
    techloan_updater = {
        'server_host': '',
        'oauth_key': 'dummy',
        'oauth_secret': 'dummy',
        'oauth_user': 'javerage',
    }

    def test_from_spotseeker_server(self):
        """
        Test that from_spotseeker_server returns a correct Spots object
        """
        spots = Spots.from_spotseeker_server(self.techloan_updater)
        self.assertIsInstance(spots, Spots)

        # TODO: check for the correct number of spots

        # TODO: check for correct spot data

        pass

    """
    The following tests test functions used in sync_with_techloan
    """
    def test_deactivate_all_items(self):
        """
        Test that deactivate_all_items updates the items with the correct data
        """

        pass

    def test_equipments_for_spot(self):
        """
        Test that equipments_for_spot returns the correct equipment data
        """

        pass

    def test_item_with_equipment_id(self):
        """
        Test that item_with_equipment_id returns the correct item data
        """

        pass

    def test_sync_equipment_to_item(self):
        """
        Test that sync_equipment_to_item updates the correct item data
        """

        pass
