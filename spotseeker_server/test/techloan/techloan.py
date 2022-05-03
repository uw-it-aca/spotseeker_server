# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import override_settings
from spotseeker_server.spotseeker_server.management.commands.\
    techloan.techloan import Techloan
from spotseeker_server.spotseeker_server.test.techloan import TechloanTestCase


@override_settings(SPOTSEEKER_TECHLOAN_URL="")
class CteApiTest(TechloanTestCase):

    def test_from_cte_api(self):
        """
        Test that from_cte_api returns a correct Techloan object
        """
        techloan = Techloan.from_cte_api()
        self.assertIsInstance(techloan, Techloan)

        pass
