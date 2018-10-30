# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spotseeker_server', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spacereview',
            name='is_deleted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='spacereview',
            name='is_published',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trustedoauthclient',
            name='bypasses_user_authorization',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trustedoauthclient',
            name='is_trusted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
