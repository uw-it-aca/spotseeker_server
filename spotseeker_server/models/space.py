from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .spot import Spot


class SpaceReview(models.Model):
    space = models.ForeignKey(Spot)
    reviewer = models.ForeignKey(User, related_name='reviewer')
    published_by = models.ForeignKey(User,
                                     related_name='published_by',
                                     null=True)
    review = models.CharField(max_length=1000, default="")
    original_review = models.CharField(max_length=1000, default="")
    rating = models.IntegerField(validators=[MaxValueValidator(5),
                                             MinValueValidator(1)]
                                 )
    date_submitted = models.DateTimeField(auto_now_add=True)
    date_published = models.DateTimeField(null=True)
    is_published = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def json_data_structure(self):
        submitted = self.date_submitted.replace(microsecond=0)

        return {
            'reviewer': self.reviewer.username,
            'review': self.review,
            'rating': self.rating,
            'date_submitted': submitted.isoformat(),
        }

    def full_json_data_structure(self):
        data = {
            'id': self.pk,
            'space_name': self.space.name,
            'space_id': self.space.pk,
            'reviewer': self.reviewer.username,
            'review': self.review,
            'rating': self.rating,
            'original_review': self.original_review,
            'date_submitted': self.date_submitted.isoformat(),
            'is_published': self.is_published,
            'is_deleted': self.is_deleted,
        }

        if self.is_published:
            data['date_published'] = self.date_published.isoformat()

        return data


class SharedSpace(models.Model):
    space = models.ForeignKey(Spot)
    user = models.CharField(max_length=16)
    sender = models.CharField(max_length=256)


class SharedSpaceRecipient(models.Model):
    shared_space = models.ForeignKey(SharedSpace)
    hash_key = models.CharField(max_length=32)
    recipient = models.CharField(max_length=256)
    user = models.CharField(max_length=16, null=True, blank=True, default=None)
    date_shared = models.DateTimeField(auto_now_add=True)
    shared_count = models.IntegerField()
    date_first_viewed = models.DateTimeField(null=True)
    viewed_count = models.IntegerField()
