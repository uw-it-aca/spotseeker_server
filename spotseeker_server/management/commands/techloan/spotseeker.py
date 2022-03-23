# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from urllib.request import urlretrieve
import tempfile
import io
import requests
from requests_oauthlib import OAuth1
from schema import Schema
from typing import Iterator
from .techloan import Techloan
from .utils import clean_html
from django.conf import settings

logger = logging.getLogger(__name__)


def sync_equipment_to_item(equipment, item):
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
        try:
            name, _ = urlretrieve(equipment["image_url"])

            item["images"] = name
            item["extended_info"]["i_image_url"] = equipment["image_url"]
        except Exception as ex:
            item["images"] = []
            logger.warning(
                "Failed to retrieve image for item with CTE ID "
                f"{equipment['id']}: {str(ex)}"
            )

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
        self._clean_counter = 0
        self._CLEAN_COUNTER_MAX = int(settings.SPOTSEEKER_SYNC_TECHLOAN_COUNT)
        for spot in spots_json_arr:
            try:
                self.spots.append(Spot(spot))
            except Exception as ex:
                logger.warning("Bad data retrieved from spotseeker " +
                               str(ex) + " from " + json.dumps(spot))

    def __iter__(self) -> Iterator[Spot]:
        return self.spots.__iter__()

    def clean_inactive_items(self):
        for spot in self:
            for item in reversed(spot['items']):
                if 'i_is_active' not in item['extended_info'] or \
                        item['extended_info']['i_is_active'] != 'true':
                    spot['items'].remove(item)

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

        if self._clean_counter >= self._CLEAN_COUNTER_MAX:
            self.clean_inactive_items()
            self._clean_counter = 0
        else:
            self._clean_counter += 1

    def _get_item_id_by_item_info(self, items: list, item_name: str,
                                  item_brand: str, item_model: str,
                                  cte_type_id: int) -> int:
        if cte_type_id is not None:
            for item in items:
                if 'cte_type_id' in item["extended_info"] and int(
                        item["extended_info"]["cte_type_id"]) == cte_type_id:
                    return item["id"]
        else:
            for item in items:
                if item["name"] == item_name and \
                        item["extended_info"]["i_brand"] == item_brand and \
                        item["extended_info"]["i_model"] == item_model:
                    return item["id"]
        return None

    def _item_image_exists(self, item_id: int, items: list) -> bool:
        for item in items:
            if item['id'] == item_id:
                return len(item['images']) > 0

    def _item_has_image(self, item_id: int, image_url, items: list) -> bool:
        for item in items:
            if item['id'] == item_id and \
                    item['extended_info']['i_image_url'] == image_url:
                return True
            elif item['id'] == item_id:
                return False
        return False

    def _get_image_id(self, image_url, items: list, item_id: int) -> int:
        for item in items:
            if item['id'] == item_id and \
                    item['extended_info']['i_image_url'] == image_url:
                return item['images'][0]['id']
        return None

    def upload_data(self):
        url = self._url.format(self._config['server_host'])
        failures = []

        for spot in self.spots:
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

            # post item images
            content = requests.get(
                f"{url}/{spot['id']}", auth=self._oauth, headers=headers
            ).json()

            for item in spot.items:
                if isinstance(item["images"], str):
                    f = open(item["images"], "rb")
                    buf = io.BytesIO(f.read())
                    files = {'image': ('image.jpg', buf)}

                    if 'cte_type_id' in item['extended_info']:
                        item_id = self._get_item_id_by_item_info(
                            content['items'], item['name'],
                            item['extended_info']['i_brand'],
                            item['extended_info']['i_model'],
                            int(item['extended_info']['cte_type_id'])
                        )
                    else:
                        item_id = self._get_item_id_by_item_info(
                            content['items'], item['name'],
                            item['extended_info']['i_brand'],
                            item['extended_info']['i_model'],
                            None
                        )

                    if item_id is None:
                        logger.error(f"Can't find item id for {item['name']}")
                        continue

                    image_exists = self._item_image_exists(
                        item_id, content['items']
                    )
                    has_image = False
                    if image_exists:
                        has_image = self._item_has_image(
                            item_id, item['extended_info']['i_image_url'],
                            content['items']
                        )

                    # if same image already exists, skip
                    if has_image:
                        continue

                    # if different image exists, delete it
                    if image_exists:
                        # find image id
                        image_id = self._get_image_id(
                            item["extended_info"]["i_image_url"],
                            content['items'],
                            item_id
                        )
                        # delete old image
                        r = requests.delete(
                            f"{url[:-5]}/item/{item_id}/image/{image_id}",
                            auth=self._oauth,
                            headers=headers,
                        )
                        if r.status_code != 200:
                            logger.error(
                                f"Can't delete old image for {item['name']}: \
                                    {r.status_code}"
                            )
                            continue

                    # post new image
                    full_url = f"{url[:-5]}/item/{item_id}/image"

                    r = requests.post(
                        full_url,
                        files=files,
                        auth=self._oauth,
                        headers=headers,
                    )
                    if r.status_code != 201:
                        raise Exception(
                            "Error uploading image: {}".format(r.status_code)
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
