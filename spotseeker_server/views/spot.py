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

    Changes
    =================================================================

    sbutler1@illinois.edu: adapt to the new RESTDispatch framework;
        add dispatch hooks and use them for extended info and
        available hours; add support for partial updates to a spot;
        add external_id support.
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

    updated_items = {}
    new_items = []
    ei_forms = {}
    original_item_json = {}

    # create the item forms and the EI forms
    for item in json_items:
        if 'extended_info' not in item:
            raise ValidationError('extended_info required for item!')

        item_form = ItemForm(item)
        item_ei_forms = return_item_ei_forms(item.pop('extended_info', {}))
        ei_forms[item_form] = item_ei_forms
        # put the item form in either new or updated items
        if 'id' in item:
            updated_items[item['id']] = item_form
            original_item_json[item_form] = item
        else:
            new_items.append(item_form)

    # validate the new items
    for item in new_items:
        if not item.is_valid():
            raise RESTFormInvalidError(item)

    # validate the updated items
    for item_id in updated_items:
        item = updated_items[item_id]
        if not item.is_valid():
            raise RESTFormInvalidError(item)

    # stash the data
    stash['new_items'] = new_items
    stash['updated_items'] = updated_items
    stash['items_ei'] = ei_forms
    stash['original_item_json'] = original_item_json


def return_item_ei_forms(ei_json):
    """Takes in a JSON dict of EI keys and values, and returns forms"""
    forms = []

    for key, value in ei_json.iteritems():
        ei = {
            "key": key,
            "value": value
        }

        forms.append(ItemExtendedInfoForm(ei))

    return forms


@django.dispatch.receiver(
    spot_pre_save,
    dispatch_uid='spotseeker_server.views.spot.build_available_hours')
def _build_available_hours(sender, **kwargs):
    """Save the available hours for later"""
    json_values = kwargs['json_values']
    stash = kwargs['stash']

    stash['available_hours'] = json_values.pop('available_hours', None)


@django.dispatch.receiver(
    spot_pre_save,
    dispatch_uid='spotseeker_server.views.spot.build_extended_info')
def _build_extended_info(sender, **kwargs):
    """Get the new and old extended info dicts, returned as tuples"""
    json_values = kwargs['json_values']
    spot = kwargs['spot']
    stash = kwargs['stash']

    new_extended_info = json_values.pop('extended_info', None)
    if new_extended_info is not None:
        for key in new_extended_info.keys():
            value = new_extended_info[key]
            if value is None or unicode(value) == '':
                del new_extended_info[key]

    old_extended_info = {}
    if spot is not None:
        old_extended_info = \
            dict((ei.key, ei.value) for ei in spot.spotextendedinfo_set.all())

    stash['new_extended_info'] = new_extended_info
    stash['old_extended_info'] = old_extended_info


@django.dispatch.receiver(
    spot_pre_save,
    dispatch_uid='spotseeker_server.views.spot.clean_updated_items')
def _clean_updated_items(sender, **kwargs):
    """Removes unchanged items/item EI and sets items to delete"""
    json_values = kwargs['json_values']
    stash = kwargs['stash']
    spot = kwargs['spot']

    # if we don't have any json items, then return
    if spot is None or 'updated_items' not in stash:
        return

    updated_items = stash['updated_items']

    if 'items_ei' in stash:
        items_ei = stash['items_ei']
    else:
        items_ei = []

    updated_item_models = []
    original_item_json = stash['original_item_json']

    # create the lists of items to delete
    items_to_delete = []
    item_ei_to_delete = []

    # get the old items
    old_items = spot.item_set.all()

    # create item models so we can use a hashmap for matching
    for item_id, item in updated_items.iteritems():
        updated_item = updated_items[item_id]

        item_json = original_item_json[updated_item]
        item_model = Item(name=item_json['name'],
                          category=item_json['category'],
                          subcategory=item_json['subcategory'],
                          id=item_json['id'],
                          spot=spot)
        updated_item_models.append(item_model)

    # create a hashmap to match old to new, by using old:old
    lookup_hashmap = {}

    for old_item in old_items:
        lookup_hashmap[old_item] = old_item

    equality_hashmap = {}
    # create a hashmap matching new to old
    for updated_item in updated_items:
        if updated_item in lookup_hashmap:
            equality_hashmap[updated_item] = lookup_hashmap.pop(updated_item)

    # we should delete any missing from the PUT
    for item_to_delete in lookup_hashmap:
        items_to_delete.append(item_to_delete)

    # find items that haven't been updated and remove them
    for updated_item, old_item, in equality_hashmap.iteritems():

        updated_item_form = updated_item_forms[updated_item]
        updated_item_form.instance = old_item
        updated_item_ei = items_ei[updated_items[updated_item.id]]

        # clean up the EI
        old_ei_set = old_item.itemextendedinfo_set.all()
        ei_to_remove = clean_ei(old_ei_set, item_ei[updated_item.id])
        item_ei_to_delete += ei_to_remove

        # get rid of items that are all the same without EI
        if (updated_item.name == old_item.name and
            updated_item.category == old_item.category and
            updated_item.subcategory == old_item.subcategory and
                len(items_ei[updated_item_form]) == 0):
            del updated_items[updated_item.id]

    stash['items_to_delete'] = items_to_delete
    stash['item_ei_to_delete'] = item_ei_to_delete


def clean_ei(old_ei_list, new_ei_forms):
    """Returns deleted EI keys and removes unchanged EI"""
    to_delete = []
    forms_to_remove = []
    for old_ei in old_ei_list:
        found = False

        for ei_form in new_ei_forms:
            if ei_form.fields['key'] == old_ei.key:
                found = True
                if ei_form.fields['value'] == old_ei.value:
                    forms_to_remove.append(ei_form)

        # put the EI that has been removed in to_remove for removal
        if not found:
            to_delete.append(old_ei)

    # get rid of unchanged item EI
    for form in forms_to_remove:
        new_ei_forms.remove(form)

    return to_delete


@django.dispatch.receiver(
    spot_post_save,
    dispatch_uid='spotseeker_server.views.spot.save_items')
def _save_items(sender, **kwargs):
    """Save updated and new items, and then delete items not included in PUT"""
    spot = kwargs['spot']
    stash = kwargs['stash']

    if 'new_items' not in stash:
        return

    new_items = stash['new_items']
    updated_items = stash['updated_items']

    for key, value in updated_items.iteritems():
        new_items.append(value)

    # save the new item, and set the spot
    for item_form in new_items:
        item_model = item_form.save(commit=False)
        item_model.spot = spot
        item_model.save()

        if item_form not in stash['items_ei'].keys():
            continue

        for item_ei in stash['items_ei'][item_form]:
            # save the new EI
            item_ei_model = item_ei.save(commit=False)
            item_ei_model.item = item_model
            item_ei_model.save()

    # delete items not included
    if 'items_to_delete' in stash:
        items_to_delete = stash['items_to_delete']

        for item in items_to_delete:
            item.delete()

    # delete item EI not included
    if 'items_ei_to_delete' in stash:
        item_ei_to_delete = stash['items_ei_to_delete']

        for item in item_ei_to_delete:
            ei.delete()


@django.dispatch.receiver(
    spot_post_save,
    dispatch_uid='spotseeker_server.views.spot.save_available_hours')
def _save_available_hours(sender, **kwargs):
    """Sync the available hours for the spot"""
    spot = kwargs['spot']
    partial_update = kwargs['partial_update']
    stash = kwargs['stash']

    available_hours = stash['available_hours']

    if partial_update and available_hours is None:
        return

    SpotAvailableHours.objects.filter(spot=spot).delete()

    if available_hours is not None:
        for day in SpotAvailableHours.DAY_CHOICES:
            if not day[1] in available_hours:
                continue

            day_hours = available_hours[day[1]]
            for window in day_hours:
                SpotAvailableHours.objects.create(
                    spot=spot,
                    day=day[0],
                    start_time=window[0],
                    end_time=window[1]
                )


@django.dispatch.receiver(
    spot_post_save,
    dispatch_uid='spotseeker_server.views.spot.save_extended_info')
def _save_extended_info(sender, **kwargs):
    """Sync the extended info for the spot"""
    spot = kwargs['spot']
    partial_update = kwargs['partial_update']
    stash = kwargs['stash']

    new_extended_info = stash['new_extended_info']
    old_extended_info = stash['old_extended_info']

    if new_extended_info is None:
        if not partial_update:
            SpotExtendedInfo.objects.filter(spot=spot).delete()
    else:
        # first, loop over the new extended info and either:
        # - add items that are new
        # - update items that are old
        for key in new_extended_info:
            value = new_extended_info[key]

            ei = None
            if key in old_extended_info:
                if value == old_extended_info[key]:
                    continue
                else:
                    ei = SpotExtendedInfo.objects.get(spot=spot, key=key)

            eiform = SpotExtendedInfoForm({'spot': spot.pk,
                                           'key': key,
                                           'value': value},
                                          instance=ei)
            if not eiform.is_valid():
                raise RESTFormInvalidError(eiform)

            ei = eiform.save()
        # Now loop over the different in the keys and remove old
        # items that aren't present in the new set
        for key in (set(old_extended_info.keys()) -
                    set(new_extended_info.keys())):
            try:
                ei = SpotExtendedInfo.objects.get(spot=spot, key=key)
                ei.delete()
            except SpotExtendedInfo.DoesNotExist:
                # removing something that does not exist isn't an error
                pass


class SpotView(RESTDispatch):
    """ Performs actions on a Spot at /api/v1/spot/<spot id>.
    GET returns 200 with Spot details.
    POST to /api/v1/spot with valid JSON returns 200 and creates a new Spot.
    PUT returns 200 and updates the Spot information.
    DELETE returns 200 and deletes the Spot.
    """
    @app_auth_required
    def GET(self, request, spot_id):
        spot = Spot.get_with_external(spot_id)
        response = JSONResponse(spot.json_data_structure())
        response["ETag"] = spot.etag
        return response

    @user_auth_required
    @admin_auth_required
    def POST(self, request):
        return self.build_and_save_from_input(request, None)

    @user_auth_required
    @admin_auth_required
    def PUT(self, request, spot_id):
        spot = Spot.get_with_external(spot_id)

        self.validate_etag(request, spot)

        return self.build_and_save_from_input(request, spot)

    @user_auth_required
    @admin_auth_required
    def DELETE(self, request, spot_id):
        spot = Spot.get_with_external(spot_id)

        self.validate_etag(request, spot)

        spot.delete()
        response = HttpResponse()
        response.status_code = 200
        return response

    # These are utility methods for the HTTP methods
    @transaction.commit_on_success
    def build_and_save_from_input(self, request, spot):
        body = request.read()
        try:
            json_values = json.loads(body)
        except Exception as e:
            raise RESTException("Unable to parse JSON", status_code=400)

        partial_update = False
        stash = {}
        is_new = spot is None

        spot_pre_build.send(
            sender=SpotForm.implementation(),
            request=request,
            json_values=json_values,
            spot=spot,
            partial_update=partial_update,
            stash=stash
        )

        self._build_spot_types(json_values, spot, partial_update)
        self._build_spot_location(json_values)

        spot_pre_save.send(
            sender=SpotForm.implementation(),
            request=request,
            json_values=json_values,
            spot=spot,
            partial_update=partial_update,
            stash=stash
        )

        # Remve excluded fields
        excludefields = set(SpotForm.implementation().Meta.exclude)
        for fieldname in excludefields:
            if fieldname in json_values:
                del json_values[fieldname]

        if spot is not None and partial_update:
            # Copy over the existing values
            for field in spot._meta.fields:
                if field.name in excludefields:
                    continue
                if field.name not in json_values:
                    json_values[field.name] = getattr(spot, field.name)

            # spottypes is not included in the above copy, do it manually
            if 'spottypes' not in json_values:
                json_values['spottypes'] = [t.pk for t in spot.spottypes.all()]

        form = SpotForm(json_values, instance=spot)
        if not form.is_valid():
            raise RESTFormInvalidError(form)

        spot = form.save()

        spot_post_save.send(
            sender=SpotForm.implementation(),
            request=request,
            spot=spot,
            partial_update=partial_update,
            stash=stash
        )

        # gets the current etag
        spot = Spot.get_with_external(spot.pk)

        if is_new:
            response = HttpResponse(status=201)
            response['Location'] = spot.rest_url()
        else:
            response = JSONResponse(spot.json_data_structure(), status=200)
        response["ETag"] = spot.etag

        spot_post_build.send(
            sender=SpotForm.implementation(),
            request=request,
            response=response,
            spot=spot,
            partial_update=partial_update,
            stash=stash
        )

        return response

    def _build_spot_location(self, json_values):
        """Unnest the location JSON object"""
        if 'location' in json_values:
            for key in json_values['location']:
                json_values[key] = json_values['location'][key]
            del json_values['location']

    def _build_spot_types(self, json_values, spot, partial_update):
        """Fixup the 'type' array into IDs"""
        types = json_values.pop('type', None)
        if not partial_update and types is None:
            types = ()
        elif isinstance(types, basestring):
            types = (types,)

        if not partial_update or (partial_update and types is not None):
            json_values['spottypes'] = []
            for name in types:
                try:
                    t = SpotType.objects.get(name=name)
                    json_values['spottypes'].append(t.pk)
                except:
                    pass
