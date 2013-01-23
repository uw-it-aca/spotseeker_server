from spotseeker_server.forms.spot import SpotForm
from spotseeker_server.require_auth import *
from spotseeker_server.models import *
from django.http import HttpResponse
from django.db import models
import simplejson as json


@app_auth_required
def schema_gen(request):
    """ Json data that should contain every single piece of information that any spot might contain.
        The keys will be what info spots might contains, and the values will be what the possible
        types are for the actual values. If there is a list of values (even only a list of size 1)
        those are the only values that will pass validations.
    """

    schema = {
        "uri": "uri",
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
    spot_field_array = models.get_model('spotseeker_server', 'Spot')._meta.fields
    for field in spot_field_array:
        if field.get_internal_type() in internal_type_map:
            if field.name in location_descriptors:
                schema["location"].update({field.name: internal_type_map[field.get_internal_type()]})
            else:
                schema.update({field.name: internal_type_map[field.get_internal_type()]})
        else:
            if field.name in location_descriptors:
                schema["location"].update({field.name: field.get_internal_type()})
            else:
                schema.update({field.name: field.get_internal_type()})

    # To grab info about spot images
    spot_image_field_array = models.get_model('spotseeker_server', 'SpotImage')._meta.fields
    schema_image = {}
    for field in spot_image_field_array:
        if field.get_internal_type() in internal_type_map:
            schema_image.update({field.name: internal_type_map[field.get_internal_type()]})
        else:
            schema_image.update({field.name: field.get_internal_type()})
    schema["images"].append(schema_image)

    # To grab all of the different spot types
    for spot_type in SpotType.objects.all():
        schema["type"].append(spot_type.name)

    # To grab all of the extended info
    try:
        validated_ei = SpotForm({}).validated_extended_info
        org_form_exists = True
    except:
        org_form_exists = False
    for key_dict in SpotExtendedInfo.objects.values("key").distinct():
        key = key_dict["key"]
        if org_form_exists and key in validated_ei:
            schema["extended_info"].update({key: validated_ei[key]})
        else:
            schema["extended_info"].update({key: "unicode"})

    response = HttpResponse(json.dumps(schema))
    response["Content-type"] = "application/json"
    return response
