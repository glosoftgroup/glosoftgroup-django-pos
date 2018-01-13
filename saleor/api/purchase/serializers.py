from django.utils.formats import localize
from rest_framework.serializers import (
                ModelSerializer,
                HyperlinkedIdentityField,
                SerializerMethodField,
                ValidationError,
                )

from rest_framework import serializers
from django.contrib.auth import get_user_model

from ...purchase.models import PurchaseProduct as Table

import logging

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')
User = get_user_model()


class TableListSerializer(serializers.ModelSerializer):
    unit_cost = SerializerMethodField()
    total_cost = SerializerMethodField()
    supplier_name = SerializerMethodField()
    product_name = SerializerMethodField()
    date = SerializerMethodField()

    class Meta:
        model = Table
        fields = (
            'id',
            'invoice_number',
            'product_name',
            'variant',
            'quantity',
            'unit_cost',
            'total_cost',
            'supplier_name',
            'date',
        )

    def get_product_name(self, obj):
        return obj.stock.variant.display_product()

    def get_supplier_name(self, obj):
        return obj.supplier.name

    def get_date(self, obj):
        return localize(obj.created)

    def get_unit_cost(self, obj):
        try:
            return obj.cost_price.gross
        except Exception as e:
            return 0

    def get_total_cost(self, obj):
        try:
            return obj.total_cost.gross
        except Exception as e:
            return 0


class DistinctTableListSerializer(serializers.ModelSerializer):
    purchase_url = HyperlinkedIdentityField(view_name='dashboard:sale_supplier_list')
    unit_cost = SerializerMethodField()
    total_cost = SerializerMethodField()
    total_quantity = SerializerMethodField()
    supplier_name = SerializerMethodField()
    product_name = SerializerMethodField()
    date = SerializerMethodField()

    class Meta:
        model = Table
        fields = (
                 'id',
                 'invoice_number',
                 'product_name',
                 'variant',
                 'quantity',
                 'unit_cost',
                 'total_cost',
                 'total_quantity',
                 'supplier_name',
                 'date',
                 'purchase_url'
                 )

    def get_product_name(self, obj):
        return obj.stock.variant.display_product()

    def get_date(self, obj):
        return localize(obj.created)

    def get_supplier_name(self, obj):
        try:
            return obj.supplier.name
        except:
            return ''

    def get_unit_cost(self, obj):
        try:
            return obj.cost_price.gross
        except Exception as e:
            return 0

    def get_total_quantity(self, obj):
        try:
            return Table.objects.total_quantity(obj)
        except:
            return 0

    def get_total_cost(self, obj):
        try:
            return Table.objects.total_cost(obj)
        except:
            return 0


