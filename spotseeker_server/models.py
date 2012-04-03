from django.db import models
import hashlib
import time
import random

class Spot(models.Model):
    name = models.CharField(max_length=100)
    etag = models.CharField(max_length=40)
    capacity = models.CharField(max_length=50)
    display_hours_available = models.CharField(max_length=200)
    display_access_restrictions = models.CharField(max_length=200)
    organization = models.CharField(max_length=50)
    manager = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)

    def rest_url(self):
        return "/api/v1/spot/{0}".format(self.pk)

    def json_data_structure(self):
        extended_info = {}
        info = SpotExtendedInfo.objects.filter(spot=self)
        for attr in info:
            extended_info[attr.key] = attr.value

        return {
            "id": self.pk,
            "name": self.name,
            "capacity": self.capacity,
            "location": {
                "latitude": self.latitude,
                "longitude": self.longitude,
            },
            "extended_info": extended_info,
        }

    def save(self, *args, **kwargs):
        self.etag = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()
        super(Spot, self).save(*args, **kwargs)

class SpotExtendedInfo(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=200)
    spot = models.ForeignKey(Spot)

class SpotImage(models.Model):
    spot = models.ForeignKey(Spot)
    content_type = models.CharField(max_length=40)
    width = models.IntegerField()
    height = models.IntegerField()
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)

