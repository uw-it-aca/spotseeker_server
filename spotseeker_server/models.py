from django.db import models

class Spot(models.Model):
    name: models.CharField(max_length=100)
    capacity: models.CharField(max_length=50)
    display_hours_available: models.CharField(max_length=200)
    display_access_restrictions: models.CharField(max_length=200)
    organization: models.CharField(max_length=50)
    manager: models.CharField(max_length=50)

class SpotImage(models.Model):
    spot: models.ForeignKey(Spot)
    content_type: models.CharField(max_length=40)
    width: models.IntegerField()
    height: models.IntegerField()
    creation_date: models.DateTimeField(auto_now_add=True)
    modification_date: models.DateTimeField(auto_now=True)

