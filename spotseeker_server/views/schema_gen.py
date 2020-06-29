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
        adapt to the new form style.
"""

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse

from spotseeker_server.forms.spot import SpotForm
from spotseeker_server.models import *
from spotseeker_server.require_auth import *
from spotseeker_server.views.rest_dispatch import JSONResponse, RESTDispatch


class SchemaGenView(RESTDispatch):

    @app_auth_required
    def GET(self, request):
        """ Json data that should contain every single piece of information
            that any spot might contain.

            The keys will be what info spots might contains, and the values
            will be what the possible types are for the actual values. If
            there is a list of values (even only a list of size 1)
            those are the only values that will pass validations.
        """
        schema = {
            "uri": "auto",
            "available_hours": "hours_string",
            "location": {},
            "type": [],
            "extended_info": {},
            "images": [],
        }

        location_descriptors = [
            "latitude",
            "longitude",
            "height_from_sea_level",
            "building_name",
            "floor",
            "room_number"
        ]

        internal_type_map = {
            "AutoField": "int",
            "BigIntegerField": "int",
            "BooleanField": "boolean",
            "CharField": "unicode",
            "CommaSeparatedIntegerField": "unicode",
            "DateField": "date",
            "DateTimeField": "datetime",
            "DecimalField": "decimal",
            "EmailField": "unicode",
            "FileField": "unicode",
            "FilePathField": "unicode",
            "FloatField": "float",
            "ForeignKey": "unicode",
            "ImageField": "unicode",
            "IntegerField": "int",
            "IPAddressField": "unicode",
            "GenericIPAddressField": "unicode",
            "ManyToManyField": "unicode",
            "NullBooleanField": "boolean",
            "OneToOneField": "unicode",
            "PositiveIntegerField": "int",
            "PositiveSmallIntegerField": "int",
            "SlugField": "unicode",
            "SmallIntegerField": "int",
            "TextField": "unicode",
            "TimeField": "time",
            "URLField": "url",
        }

        # To grab regular spot info
        spot_field_array = \
            apps.get_model('spotseeker_server', 'Spot')._meta.fields
        for field in spot_field_array:
            if is_auto_field(field):
                schema[field.name] = 'auto'
            else:
                field_itype = field.get_internal_type()
                if field_itype in internal_type_map:
                    field_itype = internal_type_map[field_itype]

                if field.name in location_descriptors:
                    schema['location'][field.name] = field_itype
                else:
                    schema[field.name] = field_itype

        # To grab spot image info
        spot_image_field_array = apps.get_model('spotseeker_server',
                                                  'SpotImage')._meta.fields
        schema_image = {}
        for field in spot_image_field_array:
            if is_auto_field(field):
                schema_image[field.name] = 'auto'
            else:
                itype = field.get_internal_type()
                if itype in internal_type_map:
                    itype = internal_type_map[itype]
                schema_image[field.name] = itype
        schema['images'].append(schema_image)

        # To grab all of the different spot types
        for spot_type in SpotType.objects.all():
            schema["type"].append(spot_type.name)

        # To grab all of the extended info
        try:
            validated_ei = SpotForm.implementation().validated_extended_info
            org_form_exists = True
        except ImproperlyConfigured:
            org_form_exists = False
        for key_dict in SpotExtendedInfo.objects.values("key").distinct():
            key = key_dict["key"]
            if org_form_exists:
                schema['extended_info'][key] = validated_ei.get(key, 'unicode')

        return JSONResponse(schema)


def is_auto_field(field):
    # pk (id), auto_now=True, auto_now_add=True, and "etag"
    return field.auto_created or not field.editable or field.name == 'etag'
