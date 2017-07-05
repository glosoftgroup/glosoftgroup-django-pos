# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-04 08:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('nid', models.CharField(blank=True, max_length=100, null=True)),
                ('mobile', models.CharField(blank=True, max_length=100, null=True)),
                ('image', models.FileField(blank=True, null=True, upload_to='staff')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date joined')),
                ('addresses', models.ManyToManyField(blank=True, to='customer.AddressBook', verbose_name='addresses')),
                ('default_billing_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='customer.AddressBook', verbose_name='default billing address')),
                ('default_shipping_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='customer.AddressBook', verbose_name='default shipping address')),
            ],
            options={
                'verbose_name': 'supplier',
                'verbose_name_plural': 'supplier',
            },
        ),
    ]
