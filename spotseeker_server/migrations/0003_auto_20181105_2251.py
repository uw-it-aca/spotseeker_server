# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotseeker_server', '0002_auto_20181029_2244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spot',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='spot',
            name='spottypes',
            field=models.ManyToManyField(related_name='spots', max_length=50, to='spotseeker_server.SpotType', blank=True),
        ),
    ]
