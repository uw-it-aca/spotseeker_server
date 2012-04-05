from django.db import models
import hashlib
import time
import random
from PIL import Image

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

class SpotAvailableHours(models.Model):
    spot = models.ForeignKey(Spot)
    day = models.CharField(max_length=3, choices = (
        ('m', 'monday'),
        ('t', 'tuesday'),
        ('w', 'wednesday'),
        ('th', 'thursday'),
        ('f', 'friday'),
        ('sa', 'saturday'),
        ('su', 'sunday'),
    ), null=False, blank=False)

    start_time = models.TimeField()
    end_time = models.TimeField()

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.start_time >= self.end_time:
            raise Exception("Invalid time range - start time must be before end time")
        if not self.day:
            # XXX - why is this needed?  come on, django
            raise Exception("You must have a day")
        super(SpotAvailableHours, self).save(*args, **kwargs)

class SpotExtendedInfo(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=200)
    spot = models.ForeignKey(Spot)

class UploadTestImage(models.Model):
    image = models.FileField(upload_to="upload_images")

class SpotImage(models.Model):
    description = models.CharField(max_length=200)
    image = models.FileField(upload_to="spot_images")
    spot = models.ForeignKey(Spot)
    content_type = models.CharField(max_length=40)
    width = models.IntegerField()
    height = models.IntegerField()
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    etag = models.CharField(max_length=40)


    def rest_url(self):
        return "{0}/image/{1}".format(self.spot.rest_url(), self.pk)

    def save(self, *args, **kwargs):
        self.etag = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()
        img = Image.open(self.image.path)
        self.width = img.size[0]
        self.height = img.size[1]

        content_types = { "JPEG":"image/jpeg", "GIF":"image/gif", "PNG":"image/png" }
        self.content_type = content_types[img.format]

        super(SpotImage, self).save(*args, **kwargs)


