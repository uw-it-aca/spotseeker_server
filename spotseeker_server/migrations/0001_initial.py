# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import re
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oauth_provider', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteSpot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(blank=True)),
                ('item_category', models.CharField(max_length=50, null=True)),
                ('item_subcategory', models.CharField(max_length=50, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemExtendedInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=350)),
                ('item', models.ForeignKey(blank=True, to='spotseeker_server.Item', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'Item extended info',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200, blank=True)),
                ('display_index', models.PositiveIntegerField(null=True, blank=True)),
                ('image', models.ImageField(upload_to=b'item_images')),
                ('content_type', models.CharField(max_length=40)),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('etag', models.CharField(max_length=40)),
                ('upload_user', models.CharField(max_length=40)),
                ('upload_application', models.CharField(max_length=100)),
                ('item', models.ForeignKey(to='spotseeker_server.Item', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SharedSpace',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=16)),
                ('sender', models.CharField(max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SharedSpaceRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hash_key', models.CharField(max_length=32)),
                ('recipient', models.CharField(max_length=256)),
                ('user', models.CharField(default=None, max_length=16, null=True, blank=True)),
                ('date_shared', models.DateTimeField(auto_now_add=True)),
                ('shared_count', models.IntegerField()),
                ('date_first_viewed', models.DateTimeField(null=True)),
                ('viewed_count', models.IntegerField()),
                ('shared_space', models.ForeignKey(to='spotseeker_server.SharedSpace', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SpaceReview',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('review', models.CharField(default=b'', max_length=1000)),
                ('original_review', models.CharField(default=b'', max_length=1000)),
                ('rating', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('date_submitted', models.DateTimeField(auto_now_add=True)),
                ('date_published', models.DateTimeField(null=True)),
                ('is_published', models.BooleanField()),
                ('is_deleted', models.BooleanField()),
                ('published_by', models.ForeignKey(related_name='published_by', to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
                ('reviewer', models.ForeignKey(related_name='reviewer', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Spot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('latitude', models.DecimalField(null=True, max_digits=11, decimal_places=8)),
                ('longitude', models.DecimalField(null=True, max_digits=11, decimal_places=8)),
                ('height_from_sea_level', models.DecimalField(null=True, max_digits=11, decimal_places=8, blank=True)),
                ('building_name', models.CharField(max_length=100, blank=True)),
                ('floor', models.CharField(max_length=50, blank=True)),
                ('room_number', models.CharField(max_length=25, blank=True)),
                ('capacity', models.IntegerField(null=True, blank=True)),
                ('display_access_restrictions', models.CharField(max_length=200, blank=True)),
                ('organization', models.CharField(max_length=50, blank=True)),
                ('manager', models.CharField(max_length=50, blank=True)),
                ('etag', models.CharField(max_length=40)),
                ('last_modified', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('external_id', models.CharField(null=True, default=None, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')], max_length=100, blank=True, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SpotAvailableHours',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.CharField(max_length=3, choices=[(b'm', b'monday'), (b't', b'tuesday'), (b'w', b'wednesday'), (b'th', b'thursday'), (b'f', b'friday'), (b'sa', b'saturday'), (b'su', b'sunday')])),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('spot', models.ForeignKey(to='spotseeker_server.Spot', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'Spot available hours',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SpotExtendedInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=350)),
                ('spot', models.ForeignKey(to='spotseeker_server.Spot', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'Spot extended info',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SpotImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200, blank=True)),
                ('display_index', models.PositiveIntegerField(null=True, blank=True)),
                ('image', models.ImageField(upload_to=b'space_images')),
                ('content_type', models.CharField(max_length=40)),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('etag', models.CharField(max_length=40)),
                ('upload_user', models.CharField(max_length=40)),
                ('upload_application', models.CharField(max_length=100)),
                ('spot', models.ForeignKey(to='spotseeker_server.Spot', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SpotType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrustedOAuthClient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_trusted', models.BooleanField()),
                ('bypasses_user_authorization', models.BooleanField()),
                ('consumer', models.ForeignKey(to='oauth_provider.Consumer', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'Trusted OAuth clients',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='spotextendedinfo',
            unique_together=set([('spot', 'key')]),
        ),
        migrations.AddField(
            model_name='spot',
            name='spottypes',
            field=models.ManyToManyField(related_name='spots', max_length=50, null=True, to='spotseeker_server.SpotType', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='spacereview',
            name='space',
            field=models.ForeignKey(to='spotseeker_server.Spot', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sharedspace',
            name='space',
            field=models.ForeignKey(to='spotseeker_server.Spot', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='itemextendedinfo',
            unique_together=set([('item', 'key')]),
        ),
        migrations.AddField(
            model_name='item',
            name='spot',
            field=models.ForeignKey(blank=True, to='spotseeker_server.Spot', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='favoritespot',
            name='spot',
            field=models.ForeignKey(to='spotseeker_server.Spot', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='favoritespot',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
