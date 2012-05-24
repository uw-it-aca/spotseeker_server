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
    type_name = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    height_from_sea_level = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    display_access_restrictions = models.CharField(max_length=200, blank=True)
    organization = models.CharField(max_length=50, blank=True)
    manager = models.CharField(max_length=50, blank=True)
    etag = models.CharField(max_length=40)

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
                "url": img.rest_url(),
                "content-type": img.content_type,
                "width": img.width,
                "height": img.height,
                "creation_date": format_date_time(time.mktime(img.creation_date.timetuple())),
                "modification_date": format_date_time(time.mktime(img.modification_date.timetuple())),
                "upload_user": img.upload_user,
                "upload_application": img.upload_application,
                "thumbnail_root": "{0}/thumb".format(img.rest_url()),
                "description": img.description
            })

        return {
            "id": self.pk,
            "uri": self.rest_url(),
            "name": self.name,
            "type": self.type_name,
            "location": {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "height_from_sea_level": self.height_from_sea_level,
                "building_name": "",  # Not implemented yet.
                "floor": "", # Not implemented yet.
                "room_number": "", # Not implemented yet.
                "description": "" # Not implemented yet.
            },
            "capacity": self.capacity,
            "display_access_restrictions": self.display_access_restrictions,
            "images": images,
            "available_hours": available_hours,
            "organization": self.organization,
            "manager": self.manager,
            "extended_info": extended_info
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
        return "%s: %s, %s-%s" % (self.spot, self.day, self.start_time, self.end_time)

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.start_time >= self.end_time:
            raise Exception("Invalid time range - start time must be before end time")

        other_hours = SpotAvailableHours.objects.filter(spot=self.spot, day=self.day)
        for h in other_hours:
            if h.start_time <= self.start_time <= h.end_time or self.start_time <= h.start_time <= self.end_time:
                self.start_time = min(h.start_time, self.start_time)
                self.end_time = max(h.end_time, self.end_time)
                h.delete()

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
