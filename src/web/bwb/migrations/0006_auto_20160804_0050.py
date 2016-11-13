# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-03 22:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bwb', '0005_watsonmessage_api_answer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='watson_anwer',
        ),
        migrations.AddField(
            model_name='watsonmessage',
            name='requesting_message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bwb.Message'),
        ),
    ]
