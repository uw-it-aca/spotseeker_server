from django.db import models
from django.core.exceptions import ValidationError
import hashlib
import time
import random
from PIL import Image
from cStringIO import StringIO

class Spot(models.Model):
    name = models.CharField(max_length=100)
    etag = models.CharField(max_length=40)
    capacity = models.IntegerField()
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

        available_hours = {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
            'saturday': [],
            'sunday': [],
        }

        hours = SpotAvailableHours.objects.filter(spot=self).order_by('start_time')
        for window in hours:
            available_hours[window.get_day_display()].append([window.start_time.strftime("%H:%M"), window.end_time.strftime("%H:%M")])

        return {
            "id": self.pk,
            "name": self.name,
            "capacity": self.capacity,
            "location": {
                "latitude": self.latitude,
                "longitude": self.longitude,
            },
            "extended_info": extended_info,
            "available_hours": available_hours,
        }

    def __unicode__(self):
        return self.name

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

    class Meta:
        verbose_name_plural = "Spot available hours"

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.start_time >= self.end_time:
            raise Exception("Invalid time range - start time must be before end time")
        super(SpotAvailableHours, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s: %s-%s" % (self.day, self.start_time, self.end_time)

class SpotExtendedInfo(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=200)
    spot = models.ForeignKey(Spot)

    class Meta:
        verbose_name_plural = "Spot extended info"

    def __unicode__(self):
        return "%s[%s: %s]" % (self.spot, self.key, self.value)

class SpotImage(models.Model):
    description = models.CharField(max_length=200)
    image = models.ImageField(upload_to="spot_images")
    spot = models.ForeignKey(Spot)
    content_type = models.CharField(max_length=40)
    width = models.IntegerField()
    height = models.IntegerField()
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    etag = models.CharField(max_length=40)


    def rest_url(self):
        return "{0}/image/{1}".format(self.spot.rest_url(), self.pk)

    def __unicode__(self):
        return self.description

    def save(self, *args, **kwargs):
        self.etag = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()

        content_types = { "JPEG":"image/jpeg", "GIF":"image/gif", "PNG":"image/png" }
        if self.image.file.multiple_chunks():
            img = Image.open(self.image.file.temporary_file_path())
        else:
            img = StringIO(self.image.file.read())
            img = Image.open(img)

        if not img.format in content_types:
            raise ValidationError('Not an accepted image format')

        self.content_type = content_types[img.format]

        self.width = img.size[0]
        self.height = img.size[1]

        super(SpotImage, self).save(*args, **kwargs)


