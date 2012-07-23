from django import forms
from spotseeker_server.models import Spot, SpotExtendedInfo
import simplejson as json


def validate_true(value, key):
    """ This field should only have a value of 'true'. If 'false', it shouldn't exist.
    """
    if not value == 'true':
        raise forms.ValidationError("For key %s: %s can only be 'true'" % (key, value))


def validate_choices(value, choices):
    """ Check that a value is one of a couple possible choices.
    """
    if not value in choices:
        raise forms.ValidationError("Value must be one of %s" % choices)


def validate_int(value):
    """ Ensure the value is an integer.
    """
    try:
        int(value)
    except:
        raise forms.ValidationError("Value must be an int")


def validate_uw_extended_info(value):
    # TODO: access_restrictions require access_notes to be there, reservable requires reservation_notes
    # UW Spots must have extended_info
    if value is None:
        raise forms.ValidationError("You must have an extended_info section")

    # orientation, location_description, access_notes, reserve_notes, hours_notes, may be any string
    # has_whiteboards should be 'true' or not exist
    if "has_whiteboards" in value:
        validate_true(value['has_whiteboards'], 'has_whiteboards')

    # has_outlets should be 'true' or not exist
    if "has_outlets" in value:
        validate_true(value['has_outlets'], 'has_outlets')

    # has_printing  should be 'true' or not exist
    if "has_printing" in value:
        validate_true(value['has_printing'], 'has_printing')

    # has_scanner should be 'true' or not exist
    if "has_scanner" in value:
        validate_true(value['has_scanner'], 'has_scanner')

    # has_displays should be 'true' or not exist
    if "has_displays" in value:
        validate_true(value['has_displays'], 'has_displays')

    # has_projector should be 'true' or not exist
    if "has_projector" in value:
        validate_true(value['has_projector'], 'has_projector')

    # has_computers should be 'true' or not exist
    if "has_computers" in value:
        validate_true(value['has_computers'], 'has_computers')

    # has_natural_light should be 'true' or not exist
    if "has_natural_light" in value:
        validate_true(value['has_natural_light'], 'has_natural_light')

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

    # num_computers should be an int
    if "num_computers" in value:
        validate_int(value['num_computers'])

    return True


class ExtendedInfoField(forms.Field):
    def to_python(self, value):
        if value is not None:
            for k in value.keys():
                if value[k] == '':
                    del value[k]
        return value

    def validate(self, value):
        return validate_uw_extended_info(value)


class ExtendedInfoForm(forms.ModelForm):
    class Meta:
        model = SpotExtendedInfo

    def clean_value(self):
        if validate_uw_extended_info({self.data['key']: self.data['value']}):
            return self.data['value']


class UWSpotForm(forms.Form):
    class Meta:
        model = Spot
        fields = ('name', 'capacity')

    extended_info = ExtendedInfoField()
