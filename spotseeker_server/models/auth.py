# Copyright 2024 UW-IT, University of Washington
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
        """
        creates a client credential for the client, setting it for the Client
        and returning it
        """

        raw_cred = f"{self.client_id}:{self.client_secret}"
        self.client_credential = b64encode(raw_cred.encode('utf-8'))\
            .decode('utf-8')
        return self.client_credential

    def __str__(self):
        return self.name
