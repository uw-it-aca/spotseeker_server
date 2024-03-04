# Generated by Django 2.2.28 on 2023-04-06 23:28

import django.contrib.auth.validators
import django.core.validators
from django.db import migrations
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('spotseeker_server', '0004_auto_20200702_1932'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trustedoauthclient',
            options={'verbose_name_plural': 'Trusted OAuth Clients'},
        ),
        migrations.DeleteModel(
            name="Client",
        ),
    ]
