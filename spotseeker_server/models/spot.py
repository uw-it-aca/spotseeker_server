# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

""" Changes
    =================================================================

    sbutler1@illinois.edu: add external_id support; create decorator
        for updating the etag; make spottypes not required; use
        reverse() to build URLs; re-organize some of the JSON
        serialization code; add DAY_CHOICES; add unique constraint on
        extended info (spot, key); re-work SpotImage save so that the
        proper exception is thrown on an invalid image type.
"""

from PIL import Image

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.db import models
from django.db.models import Sum, Count
from django.urls import reverse

from .utility import update_etag


class SpotType(models.Model):
    """The type of Spot."""

    name = models.SlugField(max_length=50)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()


class Spot(models.Model):
    """Represents a place for students to study."""

    name = models.CharField(max_length=100, blank=True)
    spottypes = models.ManyToManyField(
        SpotType, max_length=50, related_name="spots", blank=True
    )
    latitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    height_from_sea_level = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    building_name = models.CharField(max_length=100, blank=True)
    floor = models.CharField(max_length=50, blank=True)
    room_number = models.CharField(max_length=25, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    display_access_restrictions = models.CharField(max_length=200, blank=True)
    organization = models.CharField(max_length=50, blank=True)
    manager = models.CharField(max_length=50, blank=True)
    etag = models.CharField(max_length=40)
    last_modified = models.DateTimeField(auto_now=True)
    external_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None,
        unique=True,
        validators=[validate_slug],
    )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    def json_cache_key(self):
        return "Spot:" + str(self.id) + ":json"

    def invalidate_cache(self):
        """Remove this spot's cache entry"""
        cache.delete(self.json_cache_key())

    @update_etag
    def save(self, *args, **kwargs):
        self.invalidate_cache()
        super(Spot, self).save(*args, **kwargs)

    def rest_url(self):
        return reverse("spot", kwargs={"spot_id": self.pk})

    def json_data_structure(self):
        """
        Get a dictionary representing this spot which can be JSON encoded
        """
        # If this data is cached, and the etags match, return the cached
        # version.
        cached_entry = cache.get(self.json_cache_key())
        if cached_entry and cached_entry["etag"] == self.etag:
            return cached_entry

        extended_info = {}
        info = self.spotextendedinfo_set.all()
        for attr in info:
            extended_info[attr.key] = attr.value

        available_hours = {
            "monday": [],
            "tuesday": [],
            "wednesday": [],
            "thursday": [],
            "friday": [],
            "saturday": [],
            "sunday": [],
        }

        hours = self.spotavailablehours_set.order_by("start_time")
        for window in hours:
            available_hours[window.get_day_display()].append(
                window.json_data_structure()
            )

        images_set = self.spotimage_set.order_by("display_index")
        images = [img.json_data_structure() for img in images_set]

        types = [t.name for t in self.spottypes.all()]

        checkout_items = [
            item.json_data_structure() for item in self.item_set.all()
        ]

        spot_json = {
            "id": self.pk,
            "uri": self.rest_url(),
            "etag": self.etag,
            "name": self.name,
            "type": types,
            "location": {
                # If any changes are made to this location dict,
                # MAKE SURE to reflect those changes in the
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
            "items": checkout_items,
            "last_modified": self.last_modified.isoformat(),
            "external_id": self.external_id,
        }
        # Add this spot's data to the cache
        cache.set(self.json_cache_key(), spot_json)
        return spot_json

    def update_rating(self):
        data = self.spacereview_set.filter(
            is_published=True, is_deleted=False
        ).aggregate(total=Sum("rating"), count=Count("rating"))
        if not data["total"]:
            return

        # Round down to .5 stars:
        new_rating = int(2 * data["total"] / data["count"]) / 2.0

        # update_or_create isn't in this django version, unfortunately
        ei, created = self.spotextendedinfo_set.get_or_create(
            key="rating", defaults={"value": new_rating}
        )
        if not created:
            ei.value = new_rating
            ei.save()

        ei, created = self.spotextendedinfo_set.get_or_create(
            key="review_count", defaults={"value": data["count"]}
        )
        if not created:
            ei.value = data["count"]
            ei.save()

    def delete(self, *args, **kwargs):
        self.invalidate_cache()
        super(Spot, self).delete(*args, **kwargs)

    @classmethod
    def get_with_external(cls, spot_id):
        if spot_id and str(spot_id).startswith("external:"):
            return cls.objects.get(external_id=spot_id[9:])
        else:
            return cls.objects.get(pk=spot_id)


class FavoriteSpot(models.Model):
    """A FavoriteSpot associates a User and Spot."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)

    def json_data_structure(self):
        """Returns the JSON for the Spot that is a Favorite."""
        return self.spot.json_data_structure()

    def clean(self):
        spots = self.user.favoritespot_set.all()
        if self.spot in spots:
            raise ValidationError("This Spot has already been favorited")


class SpotAvailableHours(models.Model):
    """The hours a Spot is available, i.e. the open or closed hours for
    the building the spot is located in.
    """

    DAY_CHOICES = (
        ("m", "monday"),
        ("t", "tuesday"),
        ("w", "wednesday"),
        ("th", "thursday"),
        ("f", "friday"),
        ("sa", "saturday"),
        ("su", "sunday"),
    )

    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)

    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        verbose_name_plural = "Spot available hours"

    def __unicode__(self):
        return "%s: %s, %s-%s" % (
            self.spot.name,
            self.day,
            self.start_time,
            self.end_time,
        )

    def __str__(self):
        return self.__unicode__()

    def json_data_structure(self):
        return [
            self.start_time.strftime("%H:%M"),
            self.end_time.strftime("%H:%M"),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.start_time >= self.end_time:
            raise Exception(
                "Invalid time range - start time " "must be before end time"
            )
        other_hours = SpotAvailableHours.objects.filter(
            spot=self.spot, day=self.day
        ).exclude(id=self.id)
        for h in other_hours:
            if (
                h.start_time <= self.start_time <= h.end_time
                or self.start_time <= h.start_time <= self.end_time
            ):
                self.start_time = min(h.start_time, self.start_time)
                self.end_time = max(h.end_time, self.end_time)
                h.delete()
        self.spot.save()  # Update the spot's last_modified
        super(SpotAvailableHours, self).save(*args, **kwargs)


class SpotExtendedInfo(models.Model):
    """Additional institution-provided metadata about a spot.
    If providing custom metadata, you should provide a validator for
    that data, as well.
    """

    key = models.CharField(max_length=50)
    value = models.CharField(max_length=350)
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Spot extended info"
        unique_together = ("spot", "key")

    def __unicode__(self):
        return "%s[%s: %s]" % (self.spot.name, self.key, self.value)

    def __str__(self):
        return self.__unicode__()

    def save(self, *args, **kwargs):
        self.full_clean()
        self.spot.save()  # Update the last_modified on the spot
        super(SpotExtendedInfo, self).save(*args, **kwargs)


class SpotImage(models.Model):
    """An image of a Spot. Multiple images can be associated with a Spot,
    and Spot objects have a 'Spot.spotimage_set' method that will return
    all SpotImage objects for the Spot.
    """

    CONTENT_TYPES = {
        "JPEG": "image/jpeg",
        "GIF": "image/gif",
        "PNG": "image/png",
    }

    description = models.CharField(max_length=200, blank=True)
    display_index = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to="space_images")
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)
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

    def __str__(self):
        return self.__unicode__()

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
            "thumbnail_root": reverse(
                "spot-image-thumb",
                kwargs={"spot_id": self.spot.pk, "image_id": self.pk},
            ).rstrip("/"),
            "description": self.description,
            "display_index": self.display_index,
        }

    @update_etag
    def save(self, *args, **kwargs):
        try:
            if (
                isinstance(self.image, UploadedFile)
                and self.image.file.multiple_chunks()
            ):
                img = Image.open(self.image.file.temporary_file_path())
            else:
                img = Image.open(self.image)
        except IOError:
            raise ValidationError("Not a valid image format")

        if img.format not in SpotImage.CONTENT_TYPES:
            raise ValidationError("Not an accepted image format")

        self.content_type = SpotImage.CONTENT_TYPES[img.format]
        self.width, self.height = img.size

        self.spot.invalidate_cache()
        super(SpotImage, self).save(*args, **kwargs)

    @update_etag
    def delete(self, *args, **kwargs):
        self.spot.invalidate_cache()
        self.image.delete(save=False)
        super(SpotImage, self).delete(*args, **kwargs)

    def rest_url(self):
        return reverse(
            "spot-image", kwargs={"spot_id": self.spot.pk, "image_id": self.pk}
        )
