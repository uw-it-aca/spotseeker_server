# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models

from .spot import Spot


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
