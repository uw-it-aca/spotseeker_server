# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models

from django.contrib.auth.models import User, AbstractUser


class Client(AbstractUser):
    name = models.CharField(max_length=255)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "OAuth Clients"

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()


class TrustedOAuthClient(models.Model):
    consumer = models.ForeignKey(Client, on_delete=models.CASCADE)
    is_trusted = models.BooleanField(default=False)
    bypasses_user_authorization = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Trusted OAuth Clients"

    def __unicode__(self):
        return self.consumer.name

    def __str__(self):
        return self.__unicode__()
