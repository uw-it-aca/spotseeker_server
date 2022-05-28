# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import override_settings
from django.core.exceptions import ImproperlyConfigured
from spotseeker_server.management.commands.\
    sync_techloan import Command
from spotseeker_server.management.commands.\
    techloan.techloan import Techloan
from spotseeker_server.test.techloan import TechloanTestCase


@override_settings(SPOTSEEKER_TECHLOAN_URL="")
class TechloanTest(TechloanTestCase):

    mock_techloan_data = []

    @override_settings(SPOTSEEKER_TECHLOAN_URL="")
    def test_no_techloan_url(self):
        with self.assertRaises(ImproperlyConfigured):
            Command.get_techloan()

    def test_returns_techloan_object(self):
        techloan = Command.get_techloan()
        self.assertIsInstance(techloan, Techloan)

    def test_returns_techloan_object_with_correct_data(self):
        techloan = Command.get_techloan()
        data = techloan.equipments
        self.assertEqual(data, self.mock_techloan_data)
