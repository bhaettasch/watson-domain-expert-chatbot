# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-04 08:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bwb', '0006_auto_20160804_0050'),
    ]

    operations = [
        migrations.AddField(
            model_name='watsonmessage',
            name='answerable',
            field=models.BooleanField(default=False, verbose_name='Further reaction possible'),
        ),
    ]
