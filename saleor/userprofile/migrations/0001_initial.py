# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-28 05:09
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
import saleor.search.index


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('nid', models.CharField(blank=True, max_length=100, null=True)),
                ('mobile', models.CharField(blank=True, max_length=100, null=True)),
                ('image', models.ImageField(default='staff/user.png', upload_to='staff')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date joined')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model, saleor.search.index.Indexed),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=256, verbose_name='given name')),
                ('last_name', models.CharField(blank=True, max_length=256, verbose_name='family name')),
                ('company_name', models.CharField(blank=True, max_length=256, verbose_name='company or organization')),
                ('street_address_1', models.CharField(blank=True, max_length=256, verbose_name='address')),
                ('street_address_2', models.CharField(blank=True, max_length=256, verbose_name='address')),
                ('city', models.CharField(blank=True, max_length=256, verbose_name='city')),
                ('city_area', models.CharField(blank=True, max_length=128, verbose_name='district')),
                ('postal_code', models.CharField(blank=True, max_length=20, verbose_name='postal code')),
                ('country', django_countries.fields.CountryField(max_length=2, verbose_name='country')),
                ('country_area', models.CharField(blank=True, max_length=128, verbose_name='state or province')),
                ('phone', models.CharField(blank=True, max_length=30, verbose_name='phone number')),
            ],
            options={
                'verbose_name': 'address',
                'verbose_name_plural': 'addresses',
            },
        ),
        migrations.CreateModel(
            name='UserTrail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('action', models.CharField(blank=True, max_length=100, null=True)),
                ('now', models.DateTimeField(default=django.utils.timezone.now)),
                ('date', models.DateField(default=datetime.date.today)),
                ('crud', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='addresses',
            field=models.ManyToManyField(blank=True, to='userprofile.Address', verbose_name='addresses'),
        ),
        migrations.AddField(
            model_name='user',
            name='default_billing_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='userprofile.Address', verbose_name='default billing address'),
        ),
        migrations.AddField(
            model_name='user',
            name='default_shipping_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='userprofile.Address', verbose_name='default shipping address'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
