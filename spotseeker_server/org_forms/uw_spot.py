from django import forms
from spotseeker_server.models import Spot
import simplejson as json


class ExtendedInfoField(forms.Field):
    def validate(self, value):
        if value == None:
            raise forms.ValidationError("You must have an extended_info section")
        if not "whiteboards" in value:
            raise forms.ValidationError("You must have a whiteboard field in your extended_info section")

        return True


class UWSpotForm(forms.Form):
    class Meta:
        model = Spot
        fields = ('name', 'capacity')

    extended_info = ExtendedInfoField()
