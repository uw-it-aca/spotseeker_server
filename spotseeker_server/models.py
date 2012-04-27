from django.db import models
from django.core.exceptions import ValidationError
import hashlib
import datetime
import time
from wsgiref.handlers import format_date_time
import random
from PIL import Image
from cStringIO import StringIO
import oauth_provider.models


class Spot(models.Model):
    """ Represents a place for students to study.
    """
    name = models.CharField(max_length=100, blank=True)
    etag = models.CharField(max_length=40)
    capacity = models.IntegerField(null=True, blank=True)
    display_access_restrictions = models.CharField(max_length=200, blank=True)
    organization = models.CharField(max_length=50, blank=True)
    manager = models.CharField(max_length=50, blank=True)
    latitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.etag = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()
        super(Spot, self).save(*args, **kwargs)

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

        images = []
        spot_images = SpotImage.objects.filter(spot=self)
        for img in spot_images:
            images.append({
                "id": img.pk,
                "content-type": img.content_type,
                "description": img.description,
                "creation_date": format_date_time(time.mktime(img.creation_date.timetuple())),
                "modification_date": format_date_time(time.mktime(img.modification_date.timetuple())),
                "width": img.width,
                "height": img.height,
                "url": img.rest_url(),
                "thumbnail_root": "{0}/thumb".format(img.rest_url()),
                "upload_user": img.upload_user,
                "upload_application": img.upload_application,
            })

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
            "images": images
        }


class SpotAvailableHours(models.Model):
    """ The hours a Spot is available, i.e. the open or closed hours for the building the spot is located in.
    """
    spot = models.ForeignKey(Spot)
    day = models.CharField(max_length=3, choices=(
        ('m', 'monday'),
        ('t', 'tuesday'),
        ('w', 'wednesday'),
        ('th', 'thursday'),
        ('f', 'friday'),
        ('sa', 'saturday'),
        ('su', 'sunday'),
    ))

    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        verbose_name_plural = "Spot available hours"

    def __unicode__(self):
        return "%s: %s-%s" % (self.day, self.start_time, self.end_time)

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.start_time >= self.end_time:
            raise Exception("Invalid time range - start time must be before end time")
        super(SpotAvailableHours, self).save(*args, **kwargs)


class SpotExtendedInfo(models.Model):
    """ Additional institution-provided metadata about a spot. If providing custom metadata, you should provide a validator for that data, as well.
    """
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=200)
    spot = models.ForeignKey(Spot)

    class Meta:
        verbose_name_plural = "Spot extended info"

    def __unicode__(self):
        return "%s[%s: %s]" % (self.spot, self.key, self.value)


class SpotImage(models.Model):
    """ An image of a Spot. Multiple images can be associated with a Spot, and Spot objects have a 'Spot.spotimage_set' method that will return all SpotImage objects for the Spot.
    """
    description = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="spot_images", height_field="height",
                              width_field="width")
    spot = models.ForeignKey(Spot)
    content_type = models.CharField(max_length=40)
    width = models.IntegerField()
    height = models.IntegerField()
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    etag = models.CharField(max_length=40)
    upload_user = models.CharField(max_length=40)
    upload_application = models.CharField(max_length=100)

    def __unicode__(self):
        return self.description

    def save(self, *args, **kwargs):
        self.etag = hashlib.sha1("{0} - {1}".format(random.random(), 
                                                    time.time())).hexdigest()

        content_types = {"JPEG": "image/jpeg", "GIF": "image/gif",
                         "PNG": "image/png"}
        if self.image.file.multiple_chunks():
            img = Image.open(self.image.file.temporary_file_path())
        else:
            img = Image.open(self.image)

        if not img.format in content_types:
            raise ValidationError('Not an accepted image format')

        self.content_type = content_types[img.format]

        super(SpotImage, self).save(*args, **kwargs)

    def rest_url(self):
        return "{0}/image/{1}".format(self.spot.rest_url(), self.pk)


class TrustedOAuthClient(models.Model):
    consumer = models.ForeignKey(oauth_provider.models.Consumer)
    is_trusted = models.BooleanField()

    class Meta:
        verbose_name_plural = "Trusted OAuth clients"

    def __unicode__(self):
        return self.consumer.name
