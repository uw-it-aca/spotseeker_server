from django import forms
from spotseeker_server.models import Spot
import simplejson as json


def validate_true(value):
    """ This field should only have a value of 'true'. If 'false', it shouldn't exist.
    """
    if not value == 'true':
        raise forms.ValidationError("%s can only be 'true'" % value)


def validate_choices(value, choices):
    """ Check that a value is one of a couple possible choices.
    """
    if not value in choices:
        raise forms.ValidationError("Value must be one of %s" % choices)


class ExtendedInfoField(forms.Field):
    def validate(self, value):
        # UW Spots must have extended_info
        if value is None:
            raise forms.ValidationError("You must have an extended_info section")

        # has_whiteboards should be 'true' or not exist
        if "has_whiteboards" in value:
            validate_true(value['has_whiteboards'])

        # has_outlets should be 'true' or not exist
        if "has_outlets" in value:
            validate_true(value['has_outlets'])

        # printer_nearby should be 'true' or not exist
        if "has_printing" in value:
            validate_true(value['has_printing'])

        # has_scanner should be 'true' or not exist
        if "has_scanner" in value:
            validate_true(value['has_scanner'])

        # has_displays should be 'true' or not exist
        if "has_displays" in value:
            validate_true(value['has_displays'])

        # has_projector should be 'true' or not exist
        if "has_projector" in value:
            validate_true(value['has_projector'])

        # has_computers should be 'true' or not exist
        if "has_computers" in value:
            validate_true(value['has_computers'])

        # has_natural_light should be 'true' or not exist
        if "has_natural_light" in value:
            validate_true(value['has_natural_light'])

        # noise_level should be one of 'Silent', 'Low hum', 'Chatter', 'Rowdy', 'Variable'
        if "noise_level" in value:
            choices = ['silent', 'quiet', 'moderate', 'loud', 'variable']
            validate_choices(value['noise_level'], choices)

        # food_nearby should be one of 'In space', 'In building', 'In neighboring building', 'None nearby'
        if "food_nearby" in value:
            choices = ['space', 'building', 'neighboring']
            validate_choices(value['food_nearby'], choices)

        if "reservable" in value:
            choices = ['true', 'reservations']
            validate_choices(value['reservable'], choices)

        return True


class UWSpotForm(forms.Form):
    class Meta:
        model = Spot
        fields = ('name', 'capacity')

    extended_info = ExtendedInfoField()
