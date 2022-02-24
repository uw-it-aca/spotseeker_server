# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from urllib.request import urlretrieve
import tempfile
# from uw_spotseeker import Spotseeker
import requests
from requests_oauthlib import OAuth1
from schema import Schema
from typing import Iterator
from .techloan import Techloan
from .utils import clean_html

logger = logging.getLogger(__name__)


def sync_equipment_to_item(equipment, item):
    item["id"] = equipment["id"]
    if equipment["name"]:
        item["name"] = equipment["name"][:50]

    item["category"] = equipment["_embedded"]["class"]["category"]
    item["subcategory"] = equipment["_embedded"]["class"]["name"]

    if equipment["description"]:
        item["extended_info"]["i_description"] = clean_html(
            equipment["description"][:350])
    item["extended_info"]["i_brand"] = equipment["make"]
    item["extended_info"]["i_model"] = equipment["model"]
    if equipment["manual_url"]:
        item["extended_info"]["i_manual_url"] = equipment["manual_url"]
    if equipment["image_url"]:
        # temp_file = tempfile.TemporaryFile()

        name, img = urlretrieve(equipment["image_url"])
        # name, img = urlretrieve(equipment["image_url"], "/app/image{}.jpg".format(item["id"]))
        f = open(
            name,
            "rb"
        )
        # temp_file.write()

        # POST to images with file f with multipart/form-data
        # spot_client = Spotseeker()
        # spot_client.post_item_image(item["id"], img)

        headers = {"X-OAuth-User": "javerage"}
        auth = OAuth1("dummy",
                    "dummy")
        full_url = "http://icecream.aca.uw.edu:8001/api/v1/item/{}/image/1".format(item["id"])
        files = {'image': ('image.jpg', f)}

        r = requests.post(full_url,
                            files=files,
                            auth=auth,
                            headers=headers)
        if r.status_code != 201:
            raise Exception("Error uploading image: {}".format(r.status_code))

    item["extended_info"]["i_checkout_period"] = equipment["check_out_days"]
    if equipment["stf_funded"]:
        item["extended_info"]["i_is_stf"] = "true"
    else:
        item["extended_info"].pop("i_is_stf", None)
    item["extended_info"]["i_quantity"] = equipment["num_active"]
    item["extended_info"]["i_num_available"] = \
        equipment["_embedded"]["availability"][0]["num_available"]

    if equipment["reservable"]:
        item["extended_info"]["i_reservation_required"] = "true"
    else:
        item["extended_info"].pop("i_reservation_required", None)
    item["extended_info"]["i_access_limit_role"] = "true"
    item["extended_info"]["i_access_role_students"] = "true"


class Spot(dict):
    _scheme = Schema({
        'id': int,
        'name': str,
        'etag': str,
        'extended_info': {
            'cte_techloan_id': str,
        },
    }, ignore_extra_keys=True)

    def __init__(self, spot):
        self._scheme.validate(spot)

        # Allow the class to be accessed like a dict
        super(Spot, self).__init__(spot)
        self.__dict__ = spot

    def deactive_all_items(self):
        for item in self["items"]:
            item["extended_info"].pop("i_is_active", None)

    def item_with_equipment_id(self, equipment_id):
        for item in self['items']:
            if ('cte_type_id' in item['extended_info'] and
                    int(item['extended_info']['cte_type_id']) == equipment_id):
                return item
        return None

    def raw(self):
        return self.__dict__

    def validate(self) -> bool:
        try:
            self._scheme.validate(self.__dict__)
            return True
        except Exception as ex:
            return False


class Spots:
    _url = '{}/api/v1/spot'
    _filter = ('extended_info:app_type=tech&'
               'extended_info:has_cte_techloan=true&limit=0')

    def __init__(self, spots_json_arr, config, oauth: OAuth1):
        self._config = config
        self._oauth = oauth
        self.spots = []
        for spot in spots_json_arr:
            try:
                self.spots.append(Spot(spot))
            except Exception as ex:
                logger.warning("Bad data retrieved from spotseeker " +
                               str(ex) + " from " + json.dumps(spot))

    def __iter__(self) -> Iterator[Spot]:
        return self.spots.__iter__()

    def sync_with_techloan(self, techloan: Techloan):
        for spot in self:
            spot.deactive_all_items()
            equipments = techloan.equipments_for_spot(spot)

            for equipment in equipments:
                item = spot.item_with_equipment_id(equipment['id'])

                if item is None:
                    item = {
                        'name': "%s %s (%d day)" % (
                            equipment['make'],
                            equipment['model'],
                            equipment['check_out_days']
                        ),
                        'category': '',
                        'subcategory': '',
                        'extended_info': {
                            'cte_type_id': equipment["id"],
                        },
                    }
                    item["name"] = item["name"][:50]
                    spot["items"].append(item)

                item["extended_info"]["i_is_active"] = "true"
                sync_equipment_to_item(equipment, item)

    def upload_data(self):
        url = self._url.format(self._config['server_host'])
        failures = []

        for spot in self:
            if not spot.validate():
                logger.error(f"Malformed space id : {spot['id']}")
                continue

            headers = {
                'X-OAuth-User': self._config['oauth_user'],
                'If-Match': spot['etag'],
            }
            resp = requests.put(
                url=f"{url}/{spot['id']}",
                auth=self._oauth,
                json=spot.raw(),
                headers=headers,
            )

            if resp.status_code not in (
                requests.codes.ok,
                requests.codes.created,
            ):
                location = None
                reason = None
                try:
                    error = resp.json()
                    location = list(error)[0]
                    reason = error[location]
                except ValueError:
                    location = resp.status_code
                    reason = resp.content

                if isinstance(reason, bytes):
                    reason = reason.decode()

                failures.append({
                    'name': spot['name'],
                    'location': location,
                    'reason': reason,
                })

        if len(failures) != 0:
            errors = {}

            for failure in failures:
                if isinstance(failure['reason'], list):
                    errors.update({failure['location']: []})
                    for reason in failure['reason']:
                        errors[failure['location']].append(reason)
                else:
                    errors.update({failure['location']: failure['reason']})

            logger.warning(
                f"Errors putting to the server: \n{json.dumps(errors)}")

    @classmethod
    def from_spotseeker_server(cls, config) -> 'Spots':
        oauth = OAuth1(config['oauth_key'], config['oauth_secret'])
        headers = {
            'X-OAuth-User': config['oauth_user'],
        }
        spots_json_arr = requests.get(
            f"{cls._url.format(config['server_host'])}/?{cls._filter}",
            auth=oauth,
            headers=headers,
        ).json()
        return cls(spots_json_arr, config, oauth)
