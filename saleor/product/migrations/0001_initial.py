# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-01 09:16
from __future__ import unicode_literals

from decimal import Decimal
import django.contrib.postgres.fields.hstore
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_prices.models
import saleor.search.index
import satchless.item
import versatileimagefield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AttributeChoiceValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='display name')),
                ('slug', models.SlugField()),
                ('color', models.CharField(blank=True, max_length=7, validators=[django.core.validators.RegexValidator('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')], verbose_name='color')),
            ],
            options={
                'verbose_name': 'attribute choices value',
                'verbose_name_plural': 'attribute choices values',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='name')),
                ('slug', models.SlugField(verbose_name='slug')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('hidden', models.BooleanField(default=False, verbose_name='hidden')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='name')),
                ('description', models.TextField(verbose_name='description')),
                ('price', django_prices.models.PriceField(currency='KES', decimal_places=2, max_digits=12, verbose_name='price')),
                ('wholesale_price', django_prices.models.PriceField(blank=True, currency='KES', decimal_places=2, max_digits=12, null=True, verbose_name='Wholesale price')),
                ('available_on', models.DateField(blank=True, null=True, verbose_name='available on')),
                ('attributes', django.contrib.postgres.fields.hstore.HStoreField(default={}, verbose_name='attributes')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='updated at')),
                ('is_featured', models.BooleanField(default=False, verbose_name='is featured')),
                ('low_stock_threshold', models.IntegerField(default=Decimal('10'), validators=[django.core.validators.MinValueValidator(0)], verbose_name='low stock threshold')),
            ],
            options={
                'verbose_name': 'product',
                'verbose_name_plural': 'products',
            },
            bases=(models.Model, satchless.item.ItemRange, saleor.search.index.Indexed),
        ),
        migrations.CreateModel(
            name='ProductAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True, verbose_name='internal name')),
                ('name', models.CharField(max_length=100, verbose_name='display name')),
            ],
            options={
                'ordering': ('slug',),
                'verbose_name': 'product attribute',
                'verbose_name_plural': 'product attributes',
            },
        ),
        migrations.CreateModel(
            name='ProductClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='name')),
                ('has_variants', models.BooleanField(default=True, verbose_name='has variants')),
                ('is_shipping_required', models.BooleanField(default=False, verbose_name='is shipping required')),
            ],
            options={
                'verbose_name': 'product class',
                'verbose_name_plural': 'product classes',
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', versatileimagefield.fields.VersatileImageField(upload_to='products', verbose_name='image')),
                ('ppoi', versatileimagefield.fields.PPOIField(default='0.5x0.5', editable=False, max_length=20, verbose_name='ppoi')),
                ('alt', models.CharField(blank=True, max_length=128, verbose_name='short description')),
                ('order', models.PositiveIntegerField(editable=False, verbose_name='order')),
            ],
            options={
                'ordering': ('order',),
                'verbose_name': 'product image',
                'verbose_name_plural': 'product images',
            },
        ),
        migrations.CreateModel(
            name='ProductTax',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tax_name', models.CharField(blank=True, max_length=128, verbose_name='Tax name (optional)')),
                ('tax_label', models.CharField(blank=True, max_length=128, verbose_name='Short text printed on invoices')),
                ('tax', models.IntegerField(default=Decimal('0'), validators=[django.core.validators.MinValueValidator(0)], verbose_name='tax %')),
            ],
        ),
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku', models.CharField(max_length=32, unique=True, verbose_name='SKU')),
                ('name', models.CharField(blank=True, max_length=100, verbose_name='variant name')),
                ('price_override', django_prices.models.PriceField(blank=True, currency='KES', decimal_places=2, max_digits=12, null=True, verbose_name='price override')),
                ('wholesale_override', django_prices.models.PriceField(blank=True, currency='KES', decimal_places=2, max_digits=12, null=True, verbose_name='wholesale override')),
                ('attributes', django.contrib.postgres.fields.hstore.HStoreField(default={}, verbose_name='attributes')),
            ],
            options={
                'verbose_name': 'product variant',
                'verbose_name_plural': 'product variants',
            },
            bases=(models.Model, satchless.item.Item),
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=Decimal('1'), validators=[django.core.validators.MinValueValidator(0)], verbose_name='quantity')),
                ('quantity_allocated', models.IntegerField(default=Decimal('0'), validators=[django.core.validators.MinValueValidator(0)], verbose_name='allocated quantity')),
                ('cost_price', django_prices.models.PriceField(blank=True, currency='KES', decimal_places=2, max_digits=12, null=True, verbose_name='cost price')),
            ],
        ),
        migrations.CreateModel(
            name='StockHistoryEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='last history change')),
                ('comment', models.CharField(blank=True, default='', max_length=100, verbose_name='comment')),
                ('crud', models.CharField(blank=True, default='', max_length=30, verbose_name='crud')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='product.Stock', verbose_name='order')),
            ],
            options={
                'ordering': ('date',),
                'verbose_name': 'Stock history entry',
                'verbose_name_plural': 'Stock history entries',
            },
        ),
        migrations.CreateModel(
            name='StockLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='location')),
            ],
        ),
        migrations.CreateModel(
            name='VariantImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variant_images', to='product.ProductImage', verbose_name='image')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variant_images', to='product.ProductVariant', verbose_name='variant')),
            ],
            options={
                'verbose_name': 'variant image',
                'verbose_name_plural': 'variant images',
            },
        ),
    ]
