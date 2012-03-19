from django.forms import ModelForm
from spotseeker_server.models import Spot

class DefaultSpotForm(ModelForm):
    class Meta:
        model = Spot
        fields = ('name', 'capacity')

