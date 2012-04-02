from django import forms

class DefaultSpotSearchForm(forms.Form):
    distance = forms.FloatField(required=False)
    center_latitude = forms.FloatField(required=False)
    center_longitude = forms.FloatField(required=False)

