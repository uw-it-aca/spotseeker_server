""" Copyright 2012, 2013 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Changes
    =================================================================

    sbutler1@illinois.edu: add external_id support; create decorator
        for updating the etag; make spottypes not required; use
        reverse() to build URLs; re-organize some of the JSON
        serialization code; add DAY_CHOICES; add unique constraint on
        extended info (spot, key); re-work SpotImage save so that the
        proper exception is thrown on an invalid image type.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.core.files.uploadedfile import UploadedFile
from django.core.urlresolvers import reverse
import hashlib
import datetime
import time
from wsgiref.handlers import format_date_time
import random
from PIL import Image
from cStringIO import StringIO
import oauth_provider.models
from django.core.cache import cache
import re
from functools import wraps


def update_etag(func):
    """Any model with an ETag can decorate an instance method with
    this to have a new ETag automatically generated. It's up to the
    wrapped function, however, to call save()."""
    def _newETag(self, *args, **kwargs):
        self.etag = hashlib.sha1("{0} - {1}".format(random.random(), time.time())).hexdigest()
        return func(self, *args, **kwargs)
    return wraps(func)(_newETag)


class SpotType(models.Model):
    """ The type of Spot.
    """
    name = models.SlugField(max_length=50)

    def __unicode__(self):
        return self.name


class Spot(models.Model):
    """ Represents a place for students to study.
    """
    name = models.CharField(max_length=100, blank=True)
    spottypes = models.ManyToManyField(SpotType, max_length=50, related_name='spots', blank=True, null=True)
    latitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    height_from_sea_level = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    building_name = models.CharField(max_length=100, blank=True)
    floor = models.CharField(max_length=50, blank=True)
    room_number = models.CharField(max_length=25, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    display_access_restrictions = models.CharField(max_length=200, blank=True)
    organization = models.CharField(max_length=50, blank=True)
    manager = models.CharField(max_length=50, blank=True)
    etag = models.CharField(max_length=40)
    last_modified = models.DateTimeField(auto_now=True, auto_now_add=True)
    external_id = models.CharField(max_length=100, null=True, blank=True, default=None, unique=True, validators=[validate_slug])

    def __unicode__(self):
        return self.name

    @update_etag
    def save(self, *args, **kwargs):
        if cache.get(self.pk):
            cache.delete(self.pk)
        super(Spot, self).save(*args, **kwargs)

    def rest_url(self):
        return reverse('spot', kwargs={'spot_id': self.pk})

    def json_data_structure(self):
        spot_json = cache.get(self.pk)
        if not spot_json:
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
                available_hours[window.get_day_display()].append(window.json_data_structure())

            images = []
            for img in SpotImage.objects.filter(spot=self):
                images.append(img.json_data_structure())
            types = []
            for t in self.spottypes.all():
                types.append(t.name)

            spot_json = {
                "id": self.pk,
                "uri": self.rest_url(),
                "etag": self.etag,
                "name": self.name,
                "type": types,
                "location": {
                    # If any changes are made to this location dict, MAKE SURE to reflect those changes in the
                    # location_descriptors list in views/schema_gen.py
                    "latitude": self.latitude,
                    "longitude": self.longitude,
                    "height_from_sea_level": self.height_from_sea_level,
                    "building_name": self.building_name,
                    "floor": self.floor,
                    "room_number": self.room_number,
                },
                "capacity": self.capacity,
                "display_access_restrictions": self.display_access_restrictions,
                "images": images,
                "available_hours": available_hours,
                "organization": self.organization,
                "manager": self.manager,
                "extended_info": extended_info,
                "last_modified": self.last_modified.isoformat(),
                "external_id": self.external_id
            }
            cache.add(self.pk, spot_json)
        return spot_json

    def delete(self, *args, **kwargs):
        cache.delete(self.pk)
        super(Spot, self).delete(*args, **kwargs)

    @staticmethod
    def get_with_external(spot_id):
        if spot_id and str(spot_id).startswith('external:'):
            return Spot.objects.get(external_id=spot_id[9:])
        else:
            return Spot.objects.get(pk=spot_id)


class SpotAvailableHours(models.Model):
    """ The hours a Spot is available, i.e. the open or closed hours for the building the spot is located in.
    """
    DAY_CHOICES = (
        ('m', 'monday'),
        ('t', 'tuesday'),
        ('w', 'wednesday'),
        ('th', 'thursday'),
        ('f', 'friday'),
        ('sa', 'saturday'),
        ('su', 'sunday'),
    )

    spot = models.ForeignKey(Spot)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)

    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        verbose_name_plural = "Spot available hours"

    def __unicode__(self):
        return "%s: %s, %s-%s" % (self.spot.name, self.day, self.start_time, self.end_time)

    def json_data_structure(self):
        return [self.start_time.strftime("%H:%M"), self.end_time.strftime("%H:%M")]

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.start_time >= self.end_time:
            raise Exception("Invalid time range - start time must be before end time")
        other_hours = SpotAvailableHours.objects.filter(spot=self.spot, day=self.day).exclude(id=self.id)
        for h in other_hours:
            if h.start_time <= self.start_time <= h.end_time or self.start_time <= h.start_time <= self.end_time:
                self.start_time = min(h.start_time, self.start_time)
                self.end_time = max(h.end_time, self.end_time)
                h.delete()
        self.spot.save()  # Update the spot's last_modified
        super(SpotAvailableHours, self).save(*args, **kwargs)


class SpotExtendedInfo(models.Model):
    """ Additional institution-provided metadata about a spot. If providing custom metadata, you should provide a validator for that data, as well.
    """
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=255)
    spot = models.ForeignKey(Spot)

    class Meta:
        verbose_name_plural = "Spot extended info"
        unique_together = ('spot', 'key')

    def __unicode__(self):
        return "%s[%s: %s]" % (self.spot.name, self.key, self.value)

    def save(self, *args, **kwargs):
        self.full_clean()
        self.spot.save()  # Update the last_modified on the spot
        super(SpotExtendedInfo, self).save(*args, **kwargs)


class SpotImage(models.Model):
    """ An image of a Spot. Multiple images can be associated with a Spot, and Spot objects have a 'Spot.spotimage_set' method that will return all SpotImage objects for the Spot.
    """
    CONTENT_TYPES = {
        "JPEG": "image/jpeg",
        "GIF": "image/gif",
        "PNG": "image/png",
    }

    description = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="space_images")
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
        if self.description:
            return "%s" % self.description
        else:
            return "%s" % self.image.name

    def json_data_structure(self):
        return {
            "id": self.pk,
            "url": self.rest_url(),
            "content-type": self.content_type,
            "width": self.width,
            "height": self.height,
            "creation_date": self.creation_date.isoformat(),
            "modification_date": self.modification_date.isoformat(),
            "upload_user": self.upload_user,
            "upload_application": self.upload_application,
            "thumbnail_root": reverse('spot-image-thumb', kwargs={'spot_id': self.spot.pk, 'image_id': self.pk}).rstrip('/'),
            "description": self.description
        }

    @update_etag
    def save(self, *args, **kwargs):
        try:
            if isinstance(self.image, UploadedFile) and self.image.file.multiple_chunks():
                img = Image.open(self.image.file.temporary_file_path())
            else:
                img = Image.open(self.image)
        except:
            raise ValidationError('Not a valid image format')

        if not img.format in SpotImage.CONTENT_TYPES:
            raise ValidationError('Not an accepted image format')

        self.content_type = SpotImage.CONTENT_TYPES[img.format]
        self.width, self.height = img.size

        super(SpotImage, self).save(*args, **kwargs)

    @update_etag
    def delete(self, *args, **kwargs):
        self.image.delete(save=False)

        super(SpotImage, self).delete(*args, **kwargs)

    def rest_url(self):
        return reverse('spot-image', kwargs={'spot_id': self.spot.pk, 'image_id': self.pk})


class TrustedOAuthClient(models.Model):
    consumer = models.ForeignKey(oauth_provider.models.Consumer)
    is_trusted = models.BooleanField()

    class Meta:
        verbose_name_plural = "Trusted OAuth clients"

    def __unicode__(self):
        return self.consumer.name
