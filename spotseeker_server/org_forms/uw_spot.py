from django import forms
from spotseeker_server.models import Spot
import simplejson as json


class ExtendedInfoField(forms.Field):
    def validate(self, value):
        # UW Spots must have extended_info
        if value == None:
            raise forms.ValidationError("You must have an extended_info section")

        # has_whiteboards should be 1/0
        if "has_whiteboards" in value:
            choices = ['true', 'false']
            if not value['has_whiteboards'] in choices:
                raise forms.ValidationError("Value for has_whiteboards must be 'true' or 'false'")

        # has_outlets is required and should be 1/0
        if not "has_outlets" in value:
            raise forms.ValidationError("You must have a has_outlets field in your extended_info section")
        choices = ['true', 'false']
        if not value['has_outlets'] in choices:
            raise forms.ValidationError("Value for has_outlets must be 'true' or 'false'")

        # printer_nearby should be one of 'In space', 'In building', or 'Not available'
        if "has_printing" in value:
            choices = ['true', 'false']
            if not value['has_printing'] in choices:
                raise forms.ValidationError("Value for has_printing must be 'true', or 'false'")

        # scanner_nearby should be one of 'In space', 'In building', 'Available for checkout', or 'Not available'
        if "has_scanner" in value:
            choices = ['true', 'false']
            if not value['has_scanner'] in choices:
                raise forms.ValidationError("Value for has_scanner must be 'true', or 'false'")

        # has_displays should be 1/0
        if "has_displays" in value:
            choices = ['true', 'false']
            if not value["has_displays"] in choices:
                raise forms.ValidationError("Value for has_displays must be 'true' or 'false'")

        # projector should be 1/0
        if "has_projector" in value:
            choices = ['true', 'false']
            if not value["has_projector"] in choices:
                raise forms.ValidationError("Value for has_projector must be 'true' or 'false'")

        # computers should be an integer
        if "has_computers" in value:
            choices = ['true', 'false']
            if not value['has_computers'] in choices:
                raise forms.ValidationError("Value for has_computers must be 'true' or 'false'")

        # has_natural_light should be 1/0
        if "has_natural_light" in value:
            choices = ['true', 'false']
            if not value["has_natural_light"] in choices:
                raise forms.ValidationError("Value for has_natural_light must be 'true' or 'false'")

        # noise_level should be one of 'Silent', 'Low hum', 'Chatter', 'Rowdy', 'Variable'
        if "noise_level" in value:
            choices = ['silent', 'quiet', 'moderate', 'loud', 'variable']
            if not value["noise_level"] in choices:
                raise forms.ValidationError("Value for noise_level must be one of %s" % choices)

        # food_nearby should be one of 'In space', 'In building', 'In neighboring building', 'None nearby'
        if "food_nearby" in value:
            choices = ['space', 'building', 'neighboring', 'none']
            if not value["food_nearby"] in choices:
                raise forms.ValidationError("Value for food_nearby must be one of %s" % choices)

        # manager (of the Spot information) is required
        if "manager" not in value:
            raise forms.ValidationError("You must have a value for manager")

        # organization is required
        if "organization" not in value:
            raise forms.ValidationError("You must have a value for organization")

        if "reservable" in value:
            choices = ['true', 'reservations', 'false']
            if not value["reservable"] in choices:
                raise forms.ValidationError("Value for reservable must be one of %s" % choices)

        return True


class UWSpotForm(forms.Form):
    class Meta:
        model = Spot
        fields = ('name', 'capacity')

    extended_info = ExtendedInfoField()
