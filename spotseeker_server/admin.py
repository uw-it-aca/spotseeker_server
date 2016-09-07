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

    sbutler1@illinois.edu: use the same forms as used for REST.

"""

from django.db import models
from django.contrib import admin
from django.conf import settings
from django.utils.importlib import import_module
from spotseeker_server.models import *
from spotseeker_server.forms.spot import SpotForm, SpotExtendedInfoForm
from spotseeker_server.forms.item import ItemForm, ItemExtendedInfoForm


class SpotAdmin(admin.ModelAdmin):
    """ The admin model for a Spot.
    The ETag is excluded because it is generated on Spot save.
    """
    form = SpotForm.implementation()

    list_display = ("name",
                    "id",
                    "building_name",
                    "organization",
                    "manager",
                    "last_modified")
    list_filter = ["spottypes",
                   "building_name",
                   "organization",
                   "manager"]
    search_fields = ["name",
                     "building_name",
                     "organization",
                     "manager"]

    actions = ['delete_model']

    def get_actions(self, request):
        actions = super(SpotAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def delete_model(self, request, spots):
        if type(spots) is Spot:
            spots.delete()
        else:
            for spot in spots.all():
                spot.delete()
    delete_model.short_description = "Delete selected spots"

admin.site.register(Spot, SpotAdmin)


class SpotImageAdmin(admin.ModelAdmin):
    """ The admin model for a SpotImage.
    Content-type, width, height, and ETag are all filled in by the server on
    SpotImage save.
    """
    exclude = ('content_type', 'width', 'height', 'etag',)
    list_display = ("pk",
                    "spot",
                    "description",
                    "content_type",
                    "modification_date",)
    list_filter = ["spot"]
    actions = ['delete_model']

    def get_actions(self, request):
        actions = super(SpotImageAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def delete_model(self, request, queryset):
        if type(queryset) == SpotImage:
            queryset.delete()
        else:
            for spot_image in queryset.all():
                spot_image.delete()
    delete_model.short_description = "Delete selected spot images"

admin.site.register(SpotImage, SpotImageAdmin)


class SpotAvailableHoursAdmin(admin.ModelAdmin):
    """ The admin model for SpotAvailableHours.
    """
    list_filter = ('day', 'spot')
admin.site.register(SpotAvailableHours, SpotAvailableHoursAdmin)


class SpotExtendedInfoAdmin(admin.ModelAdmin):
    """ The admin model for SpotExtendedInfo.
    """
    form = SpotExtendedInfoForm.implementation()

    list_display = ("spot", "key", "value")
    list_editable = ["key", "value"]
    list_filter = ["key", "spot"]
admin.site.register(SpotExtendedInfo, SpotExtendedInfoAdmin)


admin.site.register(SpotType)
admin.site.register(TrustedOAuthClient)


class ItemAdmin(admin.ModelAdmin):
    """ The admin model for a Item.
    """
    form = ItemForm.implementation()

    list_display = ("name",
                    "id",
                    "slug",
                    "spot",
                    "item_category",
                    "item_subcategory")
    list_filter = ["spot",
                   "item_category",
                   "item_subcategory"]
    search_fields = ["name",
                     "slug",
                     "item_category",
                     "item_subcategory"]

admin.site.register(Item, ItemAdmin)


class ItemImageAdmin(admin.ModelAdmin):
    """ The admin model for a ItemImage.
    Content-type, width, height, and ETag are all filled in by the server on
    ItemImage save.
    """
    exclude = ('content_type', 'width', 'height')
    list_display = ("pk",
                    "item",
                    "description",
                    "content_type")
    list_filter = ["item"]
    actions = ['delete_model']

    def get_actions(self, request):
        actions = super(ItemImageAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def delete_model(self, request, queryset):
        if type(queryset) == ItemImage:
            queryset.delete()
        else:
            for item_image in queryset.all():
                item_image.delete()
    delete_model.short_description = "Delete selected item images"

admin.site.register(ItemImage, ItemImageAdmin)


class ItemExtendedInfoAdmin(admin.ModelAdmin):
    """ The admin model for ItemExtendedInfo.
    """
    form = ItemExtendedInfoForm.implementation()

    list_display = ("item", "key", "value")
    list_editable = ["key", "value"]
    list_filter = ["key", "item"]
admin.site.register(ItemExtendedInfo, ItemExtendedInfoAdmin)
