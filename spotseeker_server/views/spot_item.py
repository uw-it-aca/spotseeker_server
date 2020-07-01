""" Copyright 2012, 2013 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""

from spotseeker_server.views.rest_dispatch import \
    RESTDispatch, RESTException, RESTFormInvalidError, JSONResponse
from spotseeker_server.forms.spot import SpotForm, SpotExtendedInfoForm
from spotseeker_server.default_forms.item import DefaultItemForm as ItemForm
from spotseeker_server.default_forms.item import DefaultItemExtendedInfoForm \
    as ItemExtendedInfoForm
from spotseeker_server.models import *
from django.http import HttpResponse
from spotseeker_server.require_auth import *
from django.db import transaction
import simplejson as json
import django.dispatch
from spotseeker_server.dispatch import \
    spot_pre_build, spot_pre_save, spot_post_save, spot_post_build
from django.core.exceptions import ObjectDoesNotExist


class ItemStash(object):
    """
    This object handles the storing and validation of an Item
    """

    def __init__(self, item):

        self.json = item
        item['item_category'] = item.pop('category', None)
        item['item_subcategory'] = item.pop('subcategory', None)
        self.form = ItemForm(item)

        if not self.form.is_valid():
            raise RESTFormInvalidError(self.form)

        if 'extended_info' not in item:
            raise ValidationError('extended_info required for item!')

        ei_json = self.json['extended_info']

        self.ei_forms = []

        for key, value in ei_json.items():
            ei = {
                "key": key,
                "value": value
            }

            ei_form = ItemExtendedInfoForm(ei)
            self.ei_forms.append(ei_form)

            if not ei_form.is_valid():
                raise RESTFormInvalidError(ei_form)

    def get_form(self):
        """Returns the ItemForm used to validate the item"""
        return self.form

    def get_ei_forms(self):
        """Returns the list containing this Item's EI forms"""
        return self.ei_forms

    def remove_ei_form(self, form):
        """Removes a given EI form from ei_forms."""
        if form in self.ei_forms:
            self.ei_forms.remove(form)

    def get_json(self):
        return self.json

    def set_instance(self, instance):
        self.instance = instance
        self.form = ItemForm(self.json, instance=instance)

    def get_instance(self):
        return self.instance


@django.dispatch.receiver(
    spot_pre_build,
    dispatch_uid='spotseeker_server.views.spot.stash_items')
def _stash_items(sender, **kwargs):
    """Save the available hours for later"""
    json_values = kwargs['json_values']
    stash = kwargs['stash']

    if 'items' not in json_values:
        return

    json_items = json_values['items']

    stash['updated_items'] = []
    stash['new_items'] = []

    # create the items
    for item in json_items:
        # put the item in either new or updated items
        if 'id' in item:
            stash['updated_items'].append(ItemStash(item))
        else:
            stash['new_items'].append(ItemStash(item))


@django.dispatch.receiver(
    spot_pre_save,
    dispatch_uid='spotseeker_server.views.spot.clean_updated_items')
def _clean_updated_items(sender, **kwargs):
    """Removes unchanged items/item EI and sets items to delete"""
    json_values = kwargs['json_values']
    stash = kwargs['stash']
    spot = kwargs['spot']

    stash['items_to_delete'] = []
    stash['item_ei_to_delete'] = []

    # if we don't have any json items, then return
    if spot is None or 'updated_items' not in stash:
        return

    updated_items = stash['updated_items']

    updated_item_models = []
    updated_item_models_to_stash = {}

    # create the lists of items to delete
    items_to_delete = []
    item_ei_to_delete = []

    # get the old items
    old_items = spot.item_set.all()

    # create item models so we can use a hashmap for matching
    for item in updated_items:
        item_json = item.get_json()
        item_model = Item(name=item_json['name'],
                          item_category=item_json['item_category'],
                          item_subcategory=item_json['item_subcategory'],
                          id=item_json['id'],
                          spot=spot)
        updated_item_models.append(item_model)
        updated_item_models_to_stash[item_model] = item

    # create a hashmap to match old to new, by using old:old
    lookup_hashmap = {}

    for old_item in old_items:
        lookup_hashmap[old_item] = old_item

    equality_hashmap = {}
    # create a hashmap matching new to old
    for updated_item in updated_item_models:
        if updated_item in lookup_hashmap:
            equality_hashmap[updated_item] = lookup_hashmap.pop(updated_item)

    # we should delete any missing from the PUT
    for item_to_delete in lookup_hashmap:
        items_to_delete.append(item_to_delete)

    # find items that haven't been updated and remove them
    for updated_item_model, old_item, in equality_hashmap.items():

        updated_item = updated_item_models_to_stash[updated_item_model]
        updated_item_form = updated_item.get_form()
        updated_item.set_instance(old_item)
        updated_item_ei = updated_item.get_ei_forms()

        # clean up the EI
        old_ei_set = old_item.itemextendedinfo_set.all()
        ei_to_remove = clean_ei(old_ei_set, updated_item_ei)
        item_ei_to_delete += ei_to_remove

        # get rid of items that are all the same without EI
        if (updated_item_model.name == old_item.name and
            updated_item_model.item_category == old_item.item_category and
            updated_item_model.item_subcategory ==
            old_item.item_subcategory and
                len(updated_item_ei) == 0):
            updated_items.remove(updated_item)

    stash['items_to_delete'] = items_to_delete
    stash['item_ei_to_delete'] = item_ei_to_delete


def clean_ei(old_ei_list, new_ei_forms):
    """Returns deleted EI keys and removes unchanged EI"""
    to_delete = []
    forms_to_remove = []
    new_ei_form_keys = []

    for ei_form in new_ei_forms:
        new_ei_form_keys.append(ei_form.cleaned_data['key'])

    for old_ei in old_ei_list:
        if old_ei.key not in new_ei_form_keys:
            to_delete.append(old_ei)

    return to_delete


@django.dispatch.receiver(
    spot_post_save,
    dispatch_uid='spotseeker_server.views.spot.save_items')
def _save_items(sender, **kwargs):
    """Save updated and new items, and then delete items not included in PUT"""
    spot = kwargs['spot']
    stash = kwargs['stash']

    if ('new_items' not in stash or 'updated_items' not in stash or
            'items_to_delete' not in stash or
            'item_ei_to_delete' not in stash):
        return

    new_items = stash['new_items']
    updated_items = stash['updated_items']

    # combine new_items and updated_items now that the middleware has handled
    # them
    for item in updated_items:
        new_items.append(item)

    # save the new item, and set the spot
    for item in new_items:
        item_form = item.get_form()
        item_model = item_form.save(commit=False)
        item_model.spot = spot

        item_model.save()

        ei_forms = item.get_ei_forms()

        for item_ei in ei_forms:
            # save the new EI
            item_ei_model = item_ei.save(commit=False)
            try:
                actual_item_ei = item_model.itemextendedinfo_set.get(
                    key=item_ei_model.key)
                if actual_item_ei.value != item_ei_model.value:
                    actual_item_ei.value = item_ei_model.value
                    actual_item_ei.save()
            except ObjectDoesNotExist:
                item_ei_model.item = item_model
                item_ei_model.save()

    # delete items not included
    items_to_delete = stash['items_to_delete']

    for item in items_to_delete:
        item.delete()

    if 'item_ei_to_delete' in stash:
        item_ei_to_delete = stash['item_ei_to_delete']

        for ei in item_ei_to_delete:
            ei.delete()
