# Generated by Django 2.2.28 on 2023-04-20 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotseeker_server', '0005_auto_20230406_2328'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='access_token',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='client',
            name='client_credential',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
