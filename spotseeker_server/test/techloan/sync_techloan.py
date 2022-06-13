# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from io import StringIO
from django.test import override_settings
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
import logging
import responses

test_logger = logging.getLogger(__name__)

bad_techloan_updater = {
    'server_host': 0,
    'oauth_key': 'dummy',
    'oauth_secret': 'dummy',
    'oauth_user': 'javerage',
}

good_techloan_updater = {
    'server_host': 'https://techloan.uw.edu',
    'oauth_key': 'dummy',
    'oauth_secret': 'dummy',
    'oauth_user': 'javerage',
}

filter = Spots._filter


def remove_images(spots: list) -> list:
    spots_copy = copy.deepcopy(spots)
    for spot in spots_copy:
        for item in spot['items']:
            item['images'] = []
    return spots_copy


def remove_item_extended_info(spots: list, key: str,
                              replacement=None) -> list:
    spots_copy = copy.deepcopy(spots)
    for spot in spots_copy:
        for item in spot['items']:
            if replacement:
                item['extended_info'][key] = replacement
            else:
                item['extended_info'].pop(key)
    return spots_copy


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


class SyncTechloanTest(TechloanTestCase):
    """
    Tests to make sure that the sync_techloan management command
    works as expected.
    """

    def setUp(self):
        self.equipments = [
            {
                'id': 54321,
                'name': 'Test Equip',
                'description': None,
                'equipment_location_id': 12345,
                'make': 'Test Make',
                'model': 'Test Model',
                'manual_url': None,
                'image_url': 'www.google.com',
                'last_modified': '2021-12-13T11:22:10.717000',
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
            {
                'id': 98765,
                'name': 'Another Equip',
                'description': 'Hi',
                'equipment_location_id': 00000,
                'make': 'Test Make',
                'model': 'Test Model',
                'manual_url': None,
                'image_url': 'www.bing.com',
                'last_modified': '2021-12-13T11:22:10.717000',
                'check_out_days': 50,
                'stf_funded': True,
                'num_active': 40,
                'reservable': False,
                '_embedded': {
                    'class': {
                        'name': 'Test Class',
                        'category': 'Testing Category',
                    },
                    'availability': [{
                        'num_available': 19,
                    }],
                },
            },
        ]

        self.equip_with_img = copy.deepcopy(self.equipments)
        for equip in self.equip_with_img:
            equip['image_url'] = 'http://placehold.jp/150x150.png'

        self.mock_spot = {
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
                        "i_image_url": "http://placehold.jp/250x250.png",
                        "cte_type_id": "54321",
                    },
                    "images": [
                        {
                            "id": 124,
                            "url": "/api/v1/item/129/image/124",
                            "content-type": "image/jpeg",
                            "creation_date": ("2022-05-25T22:"
                                              "06:59.895213+00:00"),
                            "upload_user": "",
                            "upload_application": "",
                            "thumbnail_root": ("/api/v1/item/129/"
                                               "image/124/thumb"),
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

        self.mock_spots = [
            {
                'id': 1234,
                'name': 'Test Spot',
                'etag': '12345',
                'extended_info': {
                    'cte_techloan_id': '00000',
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
                            'cte_type_id': '98765',
                        },
                        'images': [],
                    }
                ],
            },
            self.mock_spot,
        ]

        self.mock_spots2 = copy.deepcopy(self.mock_spots)
        self.mock_spots_no_imgs = remove_images(self.mock_spots)
        self.mock_spots_bad_cte_ids = remove_item_extended_info(
            self.mock_spots, 'cte_type_id', replacement='-1230123'
        )

    @override_settings(SPOTSEEKER_TECHLOAN_UPDATER=bad_techloan_updater)
    def test_bad_techloan_updater(self):
        # assert a logger error is raised
        with self.assertLogs(level='ERROR') as cm:
            # add test info log so test doesn't fail if no logs
            test_logger.info('Starting full sync...')
            call_sync()
            self.assertIn('Settings misconfigured', cm.output[0])

    def test_sync_with_individual_parts(self):
        with patch('spotseeker_server.management.commands.sync_techloan'
                   '.Command.get_techloan',
                   return_value=Techloan(self.equipments)):
            techloan = Command.get_techloan()
            self.assertIsInstance(techloan, Techloan)
            other_techloan = Techloan(self.equipments)
            self.assertEqual(techloan.equipments, other_techloan.equipments)

        with patch('spotseeker_server.management.commands.sync_techloan'
                   '.Command.get_spots',
                   return_value=Spots(self.mock_spots, None, None)):
            spots = Command.get_spots()
            self.assertIsInstance(spots, Spots)
            other_spots = Spots(self.mock_spots2, None, None)
            self.assertEqual(spots.spots, other_spots.spots)

        with patch('spotseeker_server.management.commands.sync_techloan'
                   '.Command.sync_techloan_to_spots',
                   return_value=spots.sync_with_techloan(techloan)):
            Command.sync_techloan_to_spots()
            self.assertNotEqual(spots.spots, self.mock_spots2)

    @responses.activate
    def test_get_techloan_with_requests(self):
        responses.add(
            responses.GET,
            'http://techloan.test/api/v1/equipment',
            status=200,
            body=json.dumps(self.equipments),
        )

        # cannot use override_settings for SPOTSEEKER_TECHLOAN_URL
        with patch('spotseeker_server.management.commands.techloan.techloan'
                   '.Techloan._url', 'http://techloan.test/api/v1/equipment'):
            techloan = Command().get_techloan()
        self.assertIsInstance(techloan, Techloan)
        self.assertEquals(techloan.equipments, self.equipments)

    @responses.activate
    @override_settings(SPOTSEEKER_TECHLOAN_UPDATER=bad_techloan_updater)
    # cannot use override_settings for SPOTSEEKER_TECHLOAN_URL
    @patch('spotseeker_server.management.commands.techloan.spotseeker'
           '.Spots._url', 'http://techloan.test/api/v1/spot')
    def test_get_spots_with_requests(self):
        responses.add(
            responses.GET,
            'http://techloan.test/api/v1/spot/?' + filter,
            status=200,
            body=json.dumps(self.mock_spots),
        )

        spots = Command().get_spots()
        self.assertIsInstance(spots, Spots)
        self.assertEquals(spots.spots, self.mock_spots)

    def get_spot_by_id(self, spot_id, spots):
        return [spot for spot in spots if spot['id'] == spot_id][0]

    def get_spot_ids(self, spots):
        return [spot['id'] for spot in spots]

    def get_item_ids(self, spots, spot_ids=None):
        if spot_ids is None:
            return [item['id'] for spot in spots for item in spot['items']]
        else:
            return [item['id'] for spot in spots for item in spot['items']
                    if spot['id'] in spot_ids]

    def get_image_ids(self, spots, item_id):
        return [image['id'] for spot in spots for item in spot['items']
                if (item['id'] == item_id) for image in item['images']]

    @responses.activate
    @override_settings(SPOTSEEKER_TECHLOAN_UPDATER=good_techloan_updater)
    # cannot use override_settings for SPOTSEEKER_TECHLOAN_URL
    @patch('spotseeker_server.management.commands.techloan.techloan'
           '.Techloan._url', 'http://techloan.test/api/v1/equipment')
    @patch('spotseeker_server.management.commands.techloan.spotseeker'
           '.Spots._url', 'http://techloan.test/api/v1/spot')
    def test_full_sync_techloan_no_imgs(self):
        responses.add(
            responses.GET,
            'http://techloan.test/api/v1/equipment',
            status=200,
            body=json.dumps(self.equipments),
        )

        responses.add(
            responses.GET,
            f'http://techloan.test/api/v1/spot/?{filter}',
            status=200,
            body=json.dumps(self.mock_spots),
        )

        for id in self.get_spot_ids(self.mock_spots):
            responses.add(
                responses.PUT,
                f'http://techloan.test/api/v1/spot/{id}',
                status=200,
                body=json.dumps('OK'),
            )

            responses.add(
                responses.GET,
                f'http://techloan.test/api/v1/spot/{id}',
                status=200,
                body=json.dumps(self.get_spot_by_id(id, self.mock_spots)),
            )

        # assert no errors logged
        with self.assertLogs() as cm:
            # add test info log so test doesn't fail if no logs
            test_logger.info('Starting full sync...')
            call_sync()
            for out in cm.output:
                self.assertNotIn('ERROR', out)

    @responses.activate
    @override_settings(SPOTSEEKER_TECHLOAN_UPDATER=good_techloan_updater)
    # cannot use override_settings for SPOTSEEKER_TECHLOAN_URL
    @patch('spotseeker_server.management.commands.techloan.techloan'
           '.Techloan._url', 'http://techloan.test/api/v1/equipment')
    @patch('spotseeker_server.management.commands.techloan.spotseeker'
           '.Spots._url', 'http://techloan.test/api/v1/spot')
    def test_sync_add_imgs(self):
        responses.add(
            responses.GET,
            'http://techloan.test/api/v1/equipment',
            status=200,
            body=json.dumps(self.equip_with_img),
        )

        responses.add(
            responses.GET,
            f'http://techloan.test/api/v1/spot/?{filter}',
            status=200,
            body=json.dumps(self.mock_spots_no_imgs),
        )

        for id in self.get_spot_ids(self.mock_spots_no_imgs):
            responses.add(
                responses.PUT,
                f'http://techloan.test/api/v1/spot/{id}',
                status=200,
                body=json.dumps('OK'),
            )

            responses.add(
                responses.GET,
                f'http://techloan.test/api/v1/spot/{id}',
                status=200,
                body=json.dumps(
                    self.get_spot_by_id(id, self.mock_spots_no_imgs)
                ),
            )

            for item_id in self.get_item_ids(self.mock_spots_no_imgs,
                                             spot_ids=[id]):
                responses.add(
                    responses.POST,
                    f'http://techloan.test/api/v1/item/{item_id}/image',
                    status=201,
                    body=json.dumps('OK'),
                )

        # assert no errors logged
        with self.assertLogs() as cm:
            # add test info log so test doesn't fail if no logs
            test_logger.info('Starting full sync...')
            call_sync()
            for out in cm.output:
                self.assertNotIn('Failed to retrieve image', out)
                self.assertNotIn('ERROR', out)

    @responses.activate
    @override_settings(SPOTSEEKER_TECHLOAN_UPDATER=good_techloan_updater)
    # cannot use override_settings for SPOTSEEKER_TECHLOAN_URL
    @patch('spotseeker_server.management.commands.techloan.techloan'
           '.Techloan._url', 'http://techloan.test/api/v1/equipment')
    @patch('spotseeker_server.management.commands.techloan.spotseeker'
           '.Spots._url', 'http://techloan.test/api/v1/spot')
    def test_sync_replace_imgs(self):
        responses.add(
            responses.GET,
            'http://techloan.test/api/v1/equipment',
            status=200,
            body=json.dumps(self.equip_with_img),
        )

        responses.add(
            responses.GET,
            f'http://techloan.test/api/v1/spot/?{filter}',
            status=200,
            body=json.dumps(self.mock_spots),
        )

        for id in self.get_spot_ids(self.mock_spots):
            responses.add(
                responses.PUT,
                f'http://techloan.test/api/v1/spot/{id}',
                status=200,
                body=json.dumps('OK'),
            )

            responses.add(
                responses.GET,
                f'http://techloan.test/api/v1/spot/{id}',
                status=200,
                body=json.dumps(self.get_spot_by_id(id, self.mock_spots)),
            )

            for item_id in self.get_item_ids(self.mock_spots, spot_ids=[id]):
                responses.add(
                    responses.POST,
                    f'http://techloan.test/api/v1/item/{item_id}/image',
                    status=201,
                    body=json.dumps('OK'),
                )

                for image_id in self.get_image_ids(self.mock_spots, item_id):
                    responses.add(
                        responses.DELETE,
                        'http://techloan.test/api/v1/item/'
                        f'{item_id}/image/{image_id}',
                        status=200,
                        body=json.dumps('OK'),
                    )

        # assert no errors logged
        with self.assertLogs() as cm:
            # add test info log so test doesn't fail if no logs
            test_logger.info('Starting full sync...')
            call_sync()
            for out in cm.output:
                self.assertNotIn('ERROR', out)

    @responses.activate
    @override_settings(SPOTSEEKER_TECHLOAN_UPDATER=good_techloan_updater)
    # cannot use override_settings for SPOTSEEKER_TECHLOAN_URL
    @patch('spotseeker_server.management.commands.techloan.techloan'
           '.Techloan._url', 'http://techloan.test/api/v1/equipment')
    @patch('spotseeker_server.management.commands.techloan.spotseeker'
           '.Spots._url', 'http://techloan.test/api/v1/spot')
    def test_sync_bad_cte_id(self):
        responses.add(
            responses.GET,
            'http://techloan.test/api/v1/equipment',
            status=200,
            body=json.dumps(self.equip_with_img),
        )

        responses.add(
            responses.GET,
            f'http://techloan.test/api/v1/spot/?{filter}',
            status=200,
            body=json.dumps(self.mock_spots_bad_cte_ids),
        )

        for id in self.get_spot_ids(self.mock_spots_bad_cte_ids):
            responses.add(
                responses.PUT,
                f'http://techloan.test/api/v1/spot/{id}',
                status=200,
                body=json.dumps('OK'),
            )

            responses.add(
                responses.GET,
                f'http://techloan.test/api/v1/spot/{id}',
                status=200,
                body=json.dumps(
                    self.get_spot_by_id(id, self.mock_spots_bad_cte_ids)
                ),
            )

        # assert errors for bad cte logged
        with self.assertLogs(level='ERROR') as cm:
            call_sync()
            for out in cm.output:
                if 'ERROR' in out:
                    self.assertIn('Can\'t find item id', out)

    @responses.activate
    @override_settings(SPOTSEEKER_TECHLOAN_UPDATER=good_techloan_updater)
    # cannot use override_settings for SPOTSEEKER_TECHLOAN_URL
    @patch('spotseeker_server.management.commands.techloan.techloan'
           '.Techloan._url', 'http://techloan.test/api/v1/equipment')
    @patch('spotseeker_server.management.commands.techloan.spotseeker'
           '.Spots._url', 'http://techloan.test/api/v1/spot')
    def test_no_sync_for_unchanged_equips(self):
        responses.add(
            responses.GET,
            'http://techloan.test/api/v1/equipment',
            status=200,
            body=json.dumps(self.equip_with_img),
        )

        responses.add(
            responses.GET,
            f'http://techloan.test/api/v1/spot/?{filter}',
            status=200,
            body=json.dumps(self.mock_spots_bad_cte_ids),
        )

        for id in self.get_spot_ids(self.mock_spots):
            responses.add(
                responses.PUT,
                f'http://techloan.test/api/v1/spot/{id}',
                status=200,
                body=json.dumps('OK'),
            )

            responses.add(
                responses.GET,
                f'http://techloan.test/api/v1/spot/{id}',
                status=200,
                body=json.dumps(self.get_spot_by_id(id, self.mock_spots)),
            )

            for item_id in self.get_item_ids(self.mock_spots, spot_ids=[id]):
                responses.add(
                    responses.POST,
                    f'http://techloan.test/api/v1/item/{item_id}/image',
                    status=201,
                    body=json.dumps('OK'),
                )

                for image_id in self.get_image_ids(self.mock_spots, item_id):
                    responses.add(
                        responses.DELETE,
                        'http://techloan.test/api/v1/item/'
                        f'{item_id}/image/{image_id}',
                        status=200,
                        body=json.dumps('OK'),
                    )

        with self.assertLogs() as cm:
            test_logger.info('Starting full sync...')
            with patch('spotseeker_server.management.commands.sync_techloan'
                       '.Command.get_techloan',
                       return_value=Techloan(self.equip_with_img)):
                techloan = Command.get_techloan()
            with patch('spotseeker_server.management.commands.sync_techloan'
                       '.Command.get_spots',
                       return_value=Spots(self.mock_spots, None, None)):
                spots = Command.get_spots()
            with patch('spotseeker_server.management.commands.sync_techloan'
                       '.Command.sync_techloan_to_spots',
                       return_value=spots.sync_with_techloan(techloan)):
                Command.sync_techloan_to_spots(techloan, spots)
            for out in cm.output:
                self.assertNotIn('ERROR', out)

        for item_id in self.get_item_ids(self.mock_spots, spot_ids=[id]):
            responses.add(
                responses.POST,
                f'http://techloan.test/api/v1/item/{item_id}/image',
                status=500,
                body=json.dumps('OK'),
            )

            for image_id in self.get_image_ids(self.mock_spots, item_id):
                responses.add(
                    responses.DELETE,
                    'http://techloan.test/api/v1/item/'
                    f'{item_id}/image/{image_id}',
                    status=500,
                    body=json.dumps('OK'),
                )

        with self.assertLogs() as cm:
            test_logger.info('Starting full sync...')
            with patch('spotseeker_server.management.commands.sync_techloan'
                       '.Command.sync_techloan_to_spots',
                       return_value=spots.sync_with_techloan(techloan)):
                Command.sync_techloan_to_spots(techloan, spots)
            for out in cm.output:
                self.assertNotIn('ERROR', out)

    @responses.activate
    @override_settings(SPOTSEEKER_TECHLOAN_UPDATER=good_techloan_updater)
    # cannot use override_settings for SPOTSEEKER_TECHLOAN_URL
    @patch('spotseeker_server.management.commands.techloan.techloan'
           '.Techloan._url', 'http://techloan.test/api/v1/equipment')
    @patch('spotseeker_server.management.commands.techloan.spotseeker'
           '.Spots._url', 'http://techloan.test/api/v1/spot')
    def test_deactivate_spot_items_without_matching_cte_id(self):
        responses.add(
            responses.GET,
            'http://techloan.test/api/v1/equipment',
            status=200,
            body=json.dumps(self.equip_with_img),
        )

        responses.add(
            responses.GET,
            f'http://techloan.test/api/v1/spot/?{filter}',
            status=200,
            body=json.dumps(self.mock_spots_bad_cte_ids),
        )

        for id in self.get_spot_ids(self.mock_spots_bad_cte_ids):
            responses.add(
                responses.PUT,
                f'http://techloan.test/api/v1/spot/{id}',
                status=200,
                body=json.dumps('OK'),
            )

            responses.add(
                responses.GET,
                f'http://techloan.test/api/v1/spot/{id}',
                status=200,
                body=json.dumps(
                    self.get_spot_by_id(id, self.mock_spots_bad_cte_ids)
                ),
            )

        item_ids = self.get_item_ids(self.mock_spots_bad_cte_ids)
        with self.assertLogs() as cm:
            test_logger.info('Starting full sync...')
            with patch('spotseeker_server.management.commands.sync_techloan'
                       '.Command.get_techloan',
                       return_value=Techloan(self.equip_with_img)):
                techloan = Command.get_techloan()
            with patch('spotseeker_server.management.commands.sync_techloan'
                       '.Command.get_spots',
                       return_value=Spots(
                           self.mock_spots_bad_cte_ids, None, None
                       )):
                spots = Command.get_spots()
            with patch('spotseeker_server.management.commands.sync_techloan'
                       '.Command.sync_techloan_to_spots',
                       return_value=spots.sync_with_techloan(techloan)):
                Command.sync_techloan_to_spots(techloan, spots)
            for out in cm.output:
                self.assertNotIn('ERROR', out)
            for spot in spots:
                for item in spot['items']:
                    if 'id' not in item:
                        assert 'i_is_active' in item['extended_info']
                    elif item['id'] in item_ids:
                        assert 'i_is_active' not in item['extended_info']
