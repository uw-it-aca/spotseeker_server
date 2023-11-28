# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from PIL import Image

from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from .spot import Spot
from .utility import update_etag


class Item(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, blank=True)
    spot = models.ForeignKey(Spot, blank=True, null=True,
                             on_delete=models.CASCADE)
    # These need to be item_ cat/subcat due to DB issues
    item_category = models.CharField(max_length=50, null=True)
    item_subcategory = models.CharField(max_length=50, null=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    def json_data_structure(self):
        extended = {}

        for i in self.itemextendedinfo_set.all():
            extended[i.key] = i.value

        images = []

        for image in self.itemimage_set.all():
            images.append(image.json_data_structure())

        data = {
            'id': self.pk,
            'name': self.name,
            'category': self.item_category,
            'subcategory': self.item_subcategory,
            'extended_info': extended,
            'images': images
        }

        return data


class ItemExtendedInfo(models.Model):
    item = models.ForeignKey(Item, blank=True, null=True,
                             on_delete=models.CASCADE)
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=350)

    class Meta:
        verbose_name_plural = "Item extended info"
        unique_together = ('item', 'key')

    def __unicode__(self):
        return "ItemExtendedInfo ({}) - {}: {}".format(self.item,
                                                       self.key,
                                                       self.value)

    def __str__(self):
        return self.__unicode__()


class ItemImage(models.Model):
    """ An image of a Item. Multiple images can be associated with a Item,
    and Item objects have a 'Item.itemimage_set' method that will return
    all ItemImage objects for the Item.
    """
    CONTENT_TYPES = {
        "JPEG": "image/jpeg",
        "GIF": "image/gif",
        "PNG": "image/png",
    }

    description = models.CharField(max_length=200, blank=True)
    display_index = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to="item_images")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
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
            "creation_date": self.creation_date.isoformat(),
            "upload_user": self.upload_user,
            "upload_application": self.upload_application,
            "thumbnail_root": reverse('item-image-thumb',
                                      kwargs={'item_id': self.item.pk,
                                              'image_id': self.pk}
                                      ).rstrip('/'),
            "description": self.description,
            "display_index": self.display_index,
            "width": self.width,
            "height": self.height
        }

    @update_etag
    def save(self, *args, **kwargs):
        try:
            if (isinstance(self.image, UploadedFile) and
                    self.image.file.multiple_chunks()):
                img = Image.open(self.image.file.temporary_file_path())
            else:
                img = Image.open(self.image)
        except IOError:
            raise ValidationError('Not a valid image format')

        if img.format not in ItemImage.CONTENT_TYPES:
            raise ValidationError('Not an accepted image format')

        self.content_type = ItemImage.CONTENT_TYPES[img.format]
        self.width, self.height = img.size

        super(ItemImage, self).save(*args, **kwargs)

    @update_etag
    def delete(self, *args, **kwargs):
        self.image.delete(save=False)
        super(ItemImage, self).delete(*args, **kwargs)

    def rest_url(self):
        return reverse('item-image',
                       kwargs={'item_id': self.item.pk,
                               'image_id': self.pk})
