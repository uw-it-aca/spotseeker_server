# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models

from django.contrib.auth.models import User


class TrustedOAuthClient(models.Model):  # TODO: change to consumer/client
    consumer = models.ForeignKey(User, on_delete=models.CASCADE)
    is_trusted = models.BooleanField(default=False)
    bypasses_user_authorization = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Trusted OAuth clients"

    def __unicode__(self):
        return self.consumer.name

    def __str__(self):
        return self.__unicode__()
