# variant rest api serializers.py
from datetime import date
from decimal import Decimal
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...product.models import ProductVariant, Stock
from ...discount.models import Sale
from ...discount.models import get_variant_discounts
from rest_framework.serializers import (
                SerializerMethodField,
                )
User = get_user_model()


class StockSerializer(serializers.ModelSerializer):
    price = SerializerMethodField()
    minimum = SerializerMethodField()
    wholesale = SerializerMethodField()
    cost = SerializerMethodField()

    class Meta:
        model = Stock
        fields = (
                'variant',
                'quantity',
                'price',
                'minimum',
                'wholesale',
                'cost',
                 )

    def get_price(self, obj):
        try:
            return obj.price_override.gross
        except:
            return 0

    def get_minimum(self, obj):
        try:
            return obj.minimum_price.gross
        except:
            return 0

    def get_wholesale(self, obj):
        try:
            return obj.wholesale_override.gross
        except:
            return 0

    def get_cost(self, obj):
        try:
            return obj.cost_price.gross
        except:
            return 0


class VariantListSerializer(serializers.ModelSerializer):
    product_name = SerializerMethodField()
    supplier_name = SerializerMethodField()
    unit_cost = SerializerMethodField()
    cost_price = SerializerMethodField()
    low_stock_threshold = SerializerMethodField()
    quantity = SerializerMethodField()
    tax = SerializerMethodField()
    discount = SerializerMethodField()
    product_category = SerializerMethodField()
    min_price = SerializerMethodField()
    price_override = SerializerMethodField()
    attributes_list = SerializerMethodField()
    wholesale_price = SerializerMethodField()
    qty = SerializerMethodField()
    stock = StockSerializer(many=True)

    class Meta:
        model = ProductVariant
        fields = (
            'id',
            'product_name',
            'supplier_name',
            'sku',
            'qty',
            'unit_cost',
            'cost_price',
            'low_stock_threshold',
            'tax',
            'discount',
            'quantity',
            'product_category',
            'attributes_list',
            'min_price',
            'price_override',
            'wholesale_price',
            'stock'
        )

    def get_low_stock_threshold(self, obj):
        return 10

    def get_qty(self, obj):
        return 1

    def get_supplier_name(self, obj):
        try:
            return obj.variant_supplier.name
        except Exception as e:
            return ''

    def get_cost_price(self, obj):
        return obj.get_stock_cost_price()

    def get_price_override(self, obj):
        try:
            return obj.get_price_per_item().gross
        except:
            return 0

    def get_attributes_list(self, obj):
        return ProductVariant.objects.filter(pk=obj.pk).extra(select=dict(key="content_item.data -> 'attributes'"))\
                          .values('attributes').order_by('attributes')

    def get_discount(self, obj):
        today = date.today()
        try:
            price = obj.get_price_per_item().gross
        except:
            price = 0
        discounts = Sale.objects.filter(start_date__lte=today).filter(end_date__gte=today)
        discount = 0
        discount_list = get_variant_discounts(obj, discounts)
        for discount in discount_list:
            try:
                discount = discount.factor
                discount = (Decimal(discount) * Decimal(price))
            except Exception as e:
                discount = discount.amount.gross

        return discount

    def get_min_price(self, obj):
        try:
            return obj.get_min_price_per_item().gross
        except Exception as e:
            return 0

    def get_wholesale_price(self, obj):
        try:
            return obj.get_wholesale_price_per_item().gross
        except Exception as e:
            return 0

    def get_quantity(self, obj):
        quantity = obj.get_stock_quantity()
        return quantity

    def get_product_name(self, obj):
        product_name = obj.display_product()
        return product_name

    def get_unit_cost(self, obj):
        try:
            price = obj.get_price_per_item().gross
            return price
        except:
            return 0

    def get_tax(self, obj):
        if obj.product.product_tax:
            tax = obj.product.product_tax.tax
        else:
            tax = 0
        return tax

    def get_product_category(self, obj):
        product_category = obj.product_category()
        return product_category
