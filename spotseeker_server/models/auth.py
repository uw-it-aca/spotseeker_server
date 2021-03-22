from django.db import models

import oauth_provider.models


class TrustedOAuthClient(models.Model):
    consumer = models.ForeignKey(oauth_provider.models.Consumer)
    is_trusted = models.BooleanField(default=False)
    bypasses_user_authorization = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Trusted OAuth clients"

    def __unicode__(self):
        return self.consumer.name

    def __str__(self):
        return self.__unicode__()
