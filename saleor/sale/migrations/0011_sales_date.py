# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-20 02:26
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sale', '0010_auto_20170612_2052'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales',
            name='date',
            field=models.DateField(default=datetime.date(2017, 6, 20)),
        ),
    ]