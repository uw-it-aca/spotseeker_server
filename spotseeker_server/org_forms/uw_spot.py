from django import forms
from spotseeker_server.models import Spot
import simplejson as json
import re


class ExtendedInfoField(forms.Field):
    def validate(self, value):
        # UW Spots must have extended_info
        if value == None:
            raise forms.ValidationError("You must have an extended_info section")

        # has_whiteboards should be True/False
        if "has_whiteboards" in value:
            if not re.match("True|False", value['has_whiteboards']):
                raise forms.ValidationError("Value for has_whiteboards must be True or False")

        # has_outlets is required and should be True/False
        if not "has_outlets" in value:
            raise forms.ValidationError("You must have a has_outlets field in your extended_info section")
        if not re.match("True|False", value['has_outlets']):
            raise forms.ValidationError("Value for has_outlets must be 'True' or 'False'")

        # printer_nearby should be one of 'In space', 'In building', or 'Not available'
        if "printer_nearby" in value:
            if not re.match("In space|In building|Not available", value['printer_nearby']):
                raise forms.ValidationError("Value for printer_nearby must be 'In space', 'In building', or 'Not available'")

        # scanner_nearby should be one of 'In space', 'In building', 'Available for checkout', or 'Not available'
        if "scanner_nearby" in value:
            if not re.match("In space|In building|Available for checkout|Not available", value['scanner_nearby']):
                raise forms.ValidationError("Value for scanner_nearby must be 'In space', 'In building', 'Available for checkout', or 'Not available'")

        # has_displays should be True/False
        if "has_displays" in value:
            if not re.match("True|False", value["has_displays"]):
                raise forms.ValidationError("Value for has_displays must be 'True' or 'False'")

        # projector should be True/False

        # computers should be an integer

        # natural_light should be True/False

        # noise_level should be one of 'Silent', 'Low hum', 'Chatter', 'Rowdy', 'Variable'

        # food_nearby should be one of 'In space', 'In building', 'In neighboring building', 'None nearby'

        return True


class UWSpotForm(forms.Form):
    class Meta:
        model = Spot
        fields = ('name', 'capacity')

    extended_info = ExtendedInfoField()
