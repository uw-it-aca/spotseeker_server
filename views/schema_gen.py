from spotseeker_server.forms.spot import SpotForm
from spotseeker_server.require_auth import *
from spotseeker_server.models import *
from django.http import HttpResponse
import simplejson as json

@app_auth_required
def schema_gen(request):
    schema = {
        "id": "int",
        "uri": "uri",
        "name": "unicode",
        "type": [],
        "longitude": "decimal",
        "latitude": "decimal",
        "height_from_sea_level": "decimal",
        "building_name": "unicode",
        "floor": "unicode",
        "room_number": "unicode",
        "description": "unicode",
        "capacity": "int",
        "display_access_restrictions": "unicode",
        "images": [{  
                        "id": "int",
                        "url": "uri",
                        "content-type": "unicode",
                        "width": "int",
                        "height": "int",
                        "creation_date": "datetime",
                        "modification_date": "datetime",
                        "upload_user": "unicode",
                        "upload_application": "unicode",
                        "thumbnail_root": "uri",
                        "description": "unicode"
                    },
                    #...
                ],
        "available_hours": "hours_string",
        "organization": "unicode",
        "manager": "unicode",
        "last_modified": "datetime",
        "etag": "unicode",
        "extended_info": {}
    }

    for spot_type in SpotType.objects.all():
        schema["type"].append(spot_type.name)

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
