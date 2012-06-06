from django import forms
from spotseeker_server.models import Spot
import simplejson as json
import re


class ExtendedInfoField(forms.Field):
    def validate(self, value):
        # UW Spots must have extended_info
        if value == None:
            raise forms.ValidationError("You must have an extended_info section")

        # has_whiteboards should be 1/0
        if "has_whiteboards" in value:
            choices = ['1', '0']
            if not value['has_whiteboards'] in choices:
                raise forms.ValidationError("Value for has_whiteboards must be 1 or 0")

        # has_outlets is required and should be 1/0
        if not "has_outlets" in value:
            raise forms.ValidationError("You must have a has_outlets field in your extended_info section")
        choices = ['1', '0']
        if not value['has_outlets'] in choices:
            raise forms.ValidationError("Value for has_outlets must be '1' or '0'")

        # printer_nearby should be one of 'In space', 'In building', or 'Not available'
        if "printer_nearby" in value:
            choices = ['In space', 'In building', 'Not available']
            if not value['printer_nearby'] in choices:
                raise forms.ValidationError("Value for printer_nearby must be 'In space', 'In building', or 'Not available'")

        # scanner_nearby should be one of 'In space', 'In building', 'Available for checkout', or 'Not available'
        if "scanner_nearby" in value:
            choices = ['In space', 'In building', 'Available for checkout', 'Not available']
            if not value['scanner_nearby'] in choices:
                raise forms.ValidationError("Value for scanner_nearby must be 'In space', 'In building', 'Available for checkout', or 'Not available'")

        # has_displays should be 1/0
        if "has_displays" in value:
            choices = ['1', '0']
            if not value["has_displays"] in choices:
                raise forms.ValidationError("Value for has_displays must be '1' or '0'")

        # projector should be 1/0
        if "has_projector" in value:
            choices = ['1', '0']
            if not value["has_projector"] in choices:
                raise forms.ValidationError("Value for has_projector must be '1' or '0'")

        # computers should be an integer
        if "computers" in value:
            try:
                int(value["computers"])
            except ValueError:
                raise forms.ValidationError("Value for computers must be an int")

        # has_natural_light should be 1/0
        if "has_natural_light" in value:
            choices = ['1', '0']
            if not value["has_natural_light"] in choices:
                raise forms.ValidationError("Value for has_natural_light must be '1' or '0'")

        # noise_level should be one of 'Silent', 'Low hum', 'Chatter', 'Rowdy', 'Variable'
        if "noise_level" in value:
            choices = ['Silent', 'Low hum', 'Chatter', 'Rowdy', 'Variable']
            if not value["noise_level"] in choices:
                raise forms.ValidationError("Value for noise_level must be one of %s" % choices)

        # food_nearby should be one of 'In space', 'In building', 'In neighboring building', 'None nearby'
        if "food_nearby" in value:
            choices = ['In space', 'In building', 'In neighboring building', 'None nearby']
            if not value["food_nearby"] in choices:
                raise forms.ValidationError("Value for food_nearby must be one of %s" % choices)

        return True


class UWSpotForm(forms.Form):
    class Meta:
        model = Spot
        fields = ('name', 'capacity')

    extended_info = ExtendedInfoField()
