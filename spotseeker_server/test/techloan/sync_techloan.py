# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from io import StringIO
from django.test import override_settings
from django.conf import settings
from django.core.management import call_command
from spotseeker_server.management.commands.\
    sync_techloan import Command
from spotseeker_server.management.commands.\
    techloan.spotseeker import Spot, Spots
from spotseeker_server.management.commands.\
    techloan.techloan import Techloan
from spotseeker_server.test import techloan
from spotseeker_server.test.techloan import TechloanTestCase
from mock import patch
import copy
import json
import responses

bad_techloan_updater = {
    'server_host': 0,
    'oauth_key': 'dummy',
    'oauth_secret': 'dummy',
    'oauth_user': 'javerage',
}

filter = Spots._filter
spot_url = Spots._url

equipments = [
    {
        'id': 54321,
        'name': 'Test Equip',
        'description': None,
        'equipment_location_id': 12345,
        'make': 'Test Make',
        'model': 'Test Model',
        'manual_url': None,
        'image_url': 'www.google.com',
        'check_out_days': 5,
        'stf_funded': False,
        'num_active': 0,
        'reservable': True,
        '_embedded': {
            'class': {
                'name': 'Test Class',
                'category': 'Test Category',
            },
            'availability': [{
                'num_available': 0,
            }],
        },
    },
]

mock_spot = {
    "id": 28,
    "uri": "/api/v1/spot/28",
    "etag": "4b4630339c3bcfcf850148e9db9825744b213845",
    "name": "Tech Loan Office",
    "type": [
        "checkout"
    ],
    "location": {
        "latitude": 47.65347700,
        "longitude": -122.30638200,
        "height_from_sea_level": None,
        "building_name": "Kane Hall (KNE)",
        "floor": "",
        "room_number": ""
    },
    "capacity": None,
    "display_access_restrictions": "",
    "images": [],
    "available_hours": {
        "monday": [],
        "tuesday": [],
        "wednesday": [],
        "thursday": [],
        "friday": [],
        "saturday": [],
        "sunday": []
    },
    "organization": "",
    "manager": "",
    "extended_info": {
        "app_type": "tech",
        "has_cte_techloan": "true",
        "cte_techloan_id": "12345",
        "campus": "seattle"
    },
    "items": [
        {
            "id": 129,
            "name": "Apple Macbook Pro",
            "category": "Placeholder Category",
            "subcategory": "Laptop Computer",
            "extended_info": {
                "i_quantity": "10",
                "i_model": "Macbook Pro",
                "i_brand": "Apple",
                "i_check_out_period": "7",
                "i_is_active": "true",
                "cte_type_id": "54321",
            },
            "images": [
                {
                    "id": 124,
                    "url": "/api/v1/item/129/image/124",
                    "content-type": "image/jpeg",
                    "creation_date": "2022-05-25T22:06:59.895213+00:00",
                    "upload_user": "",
                    "upload_application": "",
                    "thumbnail_root": "/api/v1/item/129/image/124/thumb",
                    "description": "Macbook Pro",
                    "display_index": 0,
                    "width": 293,
                    "height": 172
                }
            ]
        },
        {
            "id": 130,
            "name": "Dell Latitude E5440",
            "category": "Placeholder Category",
            "subcategory": "Laptop Computer",
            "extended_info": {
                "i_quantity": "12",
                "i_model": "Latitude E5440",
                "i_brand": "Dell",
                "i_check_out_period": "14",
                "i_is_active": "true"
            },
            "images": []
        },
        {
            "id": 131,
            "name": "Fender Passport P-150",
            "category": "Placeholder Category",
            "subcategory": "Portable Audio System",
            "extended_info": {
                "i_quantity": "5",
                "i_model": "Passport P-150",
                "i_brand": "Fender",
                "i_check_out_period": "7",
                "i_is_active": "true"
            },
            "images": []
        }
    ],
    "last_modified": "2022-05-25T22:07:00.172197+00:00",
    "external_id": None,
}

mock_spots = [
    {
        'id': 1234,
        'name': 'Test Spot',
        'etag': '12345',
        'extended_info': {
            'cte_techloan_id': '12345',
        },
        'items': [
            {
                'id': 5000,
                'name': 'Testing Item',
                'category': 'Test Category',
                'subcategory': 'Test Subcategory',
                'extended_info': {
                    'i_quantity': '10',
                    'i_model': 'Test Model',
                },
                'images': [],
            }
        ],
    },
    mock_spot,
]

mock_spots2 = copy.deepcopy(mock_spots)


def call_sync(*args, **kwargs):
    out = StringIO()
    err = StringIO()
    call_command(
        'sync_techloan',
        *args,
        stdout=out,
        stderr=err,
        **kwargs,
    )
    return {'out': out.getvalue(), 'err': err.getvalue()}


@override_settings(SPOTSEEKER_TECHLOAN_URL="")
class SyncTechloanTest(TechloanTestCase):

    @override_settings(SPOTSEEKER_TECHLOAN_UPDATER=bad_techloan_updater)
    def test_bad_techloan_updater(self):
        # assert a logger error is raised
        with self.assertLogs(level='ERROR') as cm:
            call_sync()
            self.assertIn('Settings misconfigured', cm.output[0])

    def test_sync_with_individual_parts(self):
        with patch('spotseeker_server.management.commands.sync_techloan'
                   '.Command.get_techloan',
                   return_value=Techloan(equipments)):
            techloan = Command.get_techloan()
            self.assertIsInstance(techloan, Techloan)
            other_techloan = Techloan(equipments)
            self.assertEqual(techloan.equipments, other_techloan.equipments)

        with patch('spotseeker_server.management.commands.sync_techloan'
                   '.Command.get_spots',
                   return_value=Spots(mock_spots, None, None)):
            spots = Command.get_spots()
            self.assertIsInstance(spots, Spots)
            other_spots = Spots(mock_spots2, None, None)
            self.assertEqual(spots.spots, other_spots.spots)

        with patch('spotseeker_server.management.commands.sync_techloan'
                   '.Command.sync_techloan_to_spots',
                   return_value=spots.sync_with_techloan(techloan)):
            Command.sync_techloan_to_spots()
            self.assertNotEqual(spots.spots, mock_spots2)

    @responses.activate
    def test_get_techloan_with_requests(self):
        responses.add(**{
            'method': responses.GET,
            'url': 'http://techloan.test/api/v1/equipment',
            'status': 200,
            'content_type': 'application/json',
            'body': json.dumps(equipments),
        })

        with patch('spotseeker_server.management.commands.techloan.techloan'
                   '.Techloan._url', 'http://techloan.test/api/v1/equipment'):
            techloan = Command().get_techloan()
        self.assertIsInstance(techloan, Techloan)
        self.assertEquals(techloan.equipments, equipments)

    @responses.activate
    @override_settings(SPOTSEEKER_TECHLOAN_UPDATER=bad_techloan_updater)
    def test_get_spots_with_requests(self):
        responses.add(**{
            'method': responses.GET,
            'url': 'http://techloan.test/api/v1/spot/?' + filter,
            'status': 200,
            'content_type': 'application/json',
            'body': json.dumps(mock_spots),
        })

        with patch('spotseeker_server.management.commands.techloan.spotseeker'
                   '.Spots._url', 'http://techloan.test/api/v1/spot'):
            spots = Command().get_spots()
        self.assertIsInstance(spots, Spots)
        self.assertEquals(spots.spots, mock_spots)

    @responses.activate
    @override_settings(SPOTSEEKER_TECHLOAN_UPDATER=bad_techloan_updater)
    @patch('spotseeker_server.management.commands.techloan.techloan'
           '.Techloan._url', 'http://techloan.test/api/v1/equipment')
    @patch('spotseeker_server.management.commands.techloan.spotseeker'
           '.Spots._url', 'http://techloan.test/api/v1/spot')
    def test_full_sync_techloan(self):
        responses.add(**{
            'method': responses.GET,
            'url': 'http://techloan.test/api/v1/equipment',
            'status': 200,
            'content_type': 'application/json',
            'body': json.dumps(equipments),
        })

        responses.add(**{
            'method': responses.GET,
            'url': 'http://techloan.test/api/v1/spot/?' + filter,
            'status': 200,
            'content_type': 'application/json',
            'body': json.dumps(mock_spots),
        })
