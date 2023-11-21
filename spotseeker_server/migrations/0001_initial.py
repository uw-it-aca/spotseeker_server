# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models
import django.contrib.auth.validators
import re
from django.conf import settings
import django.core.validators
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
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
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('name', models.CharField(max_length=255)),
                ('client_id', models.CharField(max_length=255)),
                ('client_secret', models.CharField(max_length=255)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': 'OAuth Clients',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='TrustedOAuthClient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_trusted', models.BooleanField()),
                ('bypasses_user_authorization', models.BooleanField()),
                ('consumer', models.ForeignKey(to='spotseeker_server.Client', on_delete=models.CASCADE)),
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
    ]
