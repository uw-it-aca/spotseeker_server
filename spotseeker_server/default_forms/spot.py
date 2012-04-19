from django import forms
from spotseeker_server.models import Spot

class DefaultSpotForm(forms.ModelForm):
    name = forms.CharField(max_length=100)

    class Meta:
        model = Spot
        fields = ('name', 'capacity')

