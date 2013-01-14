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
        "type": [
            "study_room",
            "study_area",
            "cafe",
            "outdoor",
            "lounge",
            "computer_lounge",
            "production_studio",
            "conference_classroom",
            "open_space"
        ],
        "longitude": "decimal",
        "latitude": "decimal",
        "height_from_sea_level": "decimal",
        "building_name": "unicode",
        "floor": "unicode",
        "room_number": "unicode",
        "description": "unicode",
        "capacity": "int",
        "display_access_restrictions": "unicode",
        "images": [
                    {  
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
        "extended_info": {
            "has_whiteboards": ['true'],
            "has_outlets": ['true'],
            "has_printing": ['true'],
            "has_scanner": ['true'],
            "has_displays": ['true'],
            "has_projector": ['true'],
            "has_computers": ['true'],
            "has_natural_light": ['true'],
            "food_nearby": ['space', 'building', 'neighboring'],
            "num_computers": "int",
            "reservable": ['true', 'reservations'],
            "noise_level": ['silent', 'quiet', 'moderate', 'loud', 'variable'],
            "access_notes": "unicode",
            "hours_notes": "unicode",
            "reservation_notes": "unicode",
            "owner": "unicode",
            "orientation": "unicode",
            "location_description": "unicode"
        },
        "last_modified": "datetime"
    }

    #Spot.objects.all(), Spot.objects.iterator()
    #for every single spot:
        #for every single key: (schema.json_data_structure().iterkeys()???)
            #if the key is extended_info:
                #for every single extended_info key:
                    #if the key doesnt exist in the meta spot's extended_info:
                        #add the key to the meta spot with type(key) as the value
            #if the key doesnt exist in the meta spot:
                #add the key to the meta spot with type(key) as the value

    #response["ETag"] = schema.etag
    response = HttpResponse(json.dumps(schema))
    response["Content-type"] = "application/json"
    return response
