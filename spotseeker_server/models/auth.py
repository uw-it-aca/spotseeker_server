# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models
from django.contrib.auth.models import AbstractUser

from base64 import b64encode


class Client(AbstractUser):
    name = models.CharField(max_length=255)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    client_credential = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name_plural = "OAuth Clients"

    def get_client_credential(self) -> str:
        raw_cred = f"{self.client_id}:{self.client_secret}"
        self.client_credential = b64encode(raw_cred.encode('utf-8'))\
            .decode('utf-8')
        return self.client_credential

    def __str__(self):
        return self.name


class TrustedOAuthClient(models.Model):
    consumer = models.ForeignKey(Client, on_delete=models.CASCADE)
    is_trusted = models.BooleanField(default=False)
    bypasses_user_authorization = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Trusted OAuth Clients"

    def __str__(self):
        return self.consumer.name
