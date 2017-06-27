# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-21 05:59
from __future__ import unicode_literals

import datetime
from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_prices.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('userprofile', '0017_auto_20170620_1601'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sales',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[(b'new', 'Processing'), (b'cancelled', 'Cancelled'), (b'shipped', 'Shipped'), (b'payment-pending', 'Payment pending'), (b'fully-paid', 'Fully paid')], default=b'new', max_length=32, verbose_name='sales status')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('last_status_change', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='last status change')),
                ('language_code', models.CharField(default='en-us', max_length=35)),
                ('user_email', models.EmailField(blank=True, default='', editable=False, max_length=254, verbose_name='user email')),
                ('terminal', models.CharField(max_length=36, null=True, verbose_name='terminal')),
                ('invoice_number', models.CharField(max_length=36, null=True, verbose_name='invoice_number')),
                ('total_net', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=100, verbose_name='total net')),
                ('sub_total', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=100, verbose_name='sub total')),
                ('total_tax', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=100, verbose_name='total tax')),
                ('amount_paid', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=100, verbose_name='amount paid')),
                ('balance', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=100, verbose_name='balance')),
                ('discount_amount', django_prices.models.PriceField(blank=True, currency='KES', decimal_places=2, max_digits=12, null=True, verbose_name='discount amount')),
                ('discount_name', models.CharField(blank=True, default='', max_length=255, verbose_name='discount name')),
                ('billing_address', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='userprofile.Address', verbose_name='billing address')),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customers', to='customer.Customer', verbose_name='customer')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'ordering': ('-last_status_change',),
                'verbose_name': 'Sales',
                'verbose_name_plural': 'Sales',
            },
        ),
        migrations.CreateModel(
            name='SoldItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('sku', models.CharField(max_length=32, verbose_name='SKU')),
                ('quantity', models.IntegerField(default=Decimal('1'), validators=[django.core.validators.MinValueValidator(0)], verbose_name='quantity')),
                ('product_name', models.CharField(max_length=128, verbose_name='product name')),
                ('total_cost', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=100, verbose_name='total cost')),
                ('unit_cost', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=100, verbose_name='unit cost')),
                ('date', models.DateField(default=datetime.date(2017, 6, 21))),
                ('sales', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solditems', to='sale.Sales')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
