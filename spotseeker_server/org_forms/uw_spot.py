from django import forms
from spotseeker_server.models import Spot
import simplejson as json
import re


class ExtendedInfoField(forms.Field):
    def validate(self, value):
        # UW Spots must have extended_info
        if value == None:
            raise forms.ValidationError("You must have an extended_info section")

        # whiteboards should be True/False
        if "whiteboards" in value:
            if not re.match("True|False", value['whiteboards']):
                raise forms.ValidationError("Value for whiteboards must be True or False")

        # outlets is required and should be True/False
        if not "outlets" in value:
            raise forms.ValidationError("You must have an outlets field in your extended_info section")
        if not re.match("True|False", value['outlets']):
            raise forms.ValidationError("Value for outlets must be 'True' or 'False'")

        # printer should be one of 'In space', 'In building', or 'Not available'
        if "printer" in value:
            if not re.match("In space|In building|Not available", value['printer']):
                raise forms.ValidationError("Value for printer must be 'In space', 'In building', or 'Not available'")

        # scanner should be one of 'In space', 'In building', 'Available for checkout', or 'Not available'
        if "scanner" in value:
            if not re.match("In space|In building|Available for checkout|Not available", value['scanner']):
                raise forms.ValidationError("Value for scanner must be 'In space', 'In building', 'Available for checkout', or 'Not available'")

        # large_screen should be True/False

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
