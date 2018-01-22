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
from saleor.payment.models import PaymentOption

import logging

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')
User = get_user_model()


class TableListSerializer(serializers.ModelSerializer):
    unit_cost = SerializerMethodField()
    total_cost = SerializerMethodField()
    paid = SerializerMethodField()
    supplier_name = SerializerMethodField()
    product_name = SerializerMethodField()
    pay_option = SerializerMethodField()
    date = SerializerMethodField()
    credit_balance = SerializerMethodField()

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
            'paid',
            'credit_balance',
            'supplier_name',
            'pay_option',
            'date',
        )

    def get_pay_option(self, obj):
        try:
            options = obj.payment_options.first().name
        except Exception as e:
            print(e)
            options = ''
        try:
            return options + '<br> ' + obj.payment_number
        except:
            return ''

    def get_credit_balance(self, obj):
        try:
            return "{:,}".format(obj.balance.gross)
        except Exception as e:
            print(e)
            return ''

    def get_paid(self, obj):
        try:
            return "{:,}".format(obj.amount_paid.gross)
        except Exception as e:
            print(e)
            return ''

    def get_product_name(self, obj):
        try:
            return obj.stock.variant.display_product()
        except:
            return ''

    def get_supplier_name(self, obj):
        try:
            return obj.supplier.name
        except:
            return ''

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


class PaymentOptionListSerializer(serializers.ModelSerializer):
    tendered = SerializerMethodField()
    transaction_number = SerializerMethodField()
    payment_name = SerializerMethodField()

    class Meta:
        model = PaymentOption
        fields = (
                'id',
                'name',
                'transaction_number',
                'payment_name',
                'tendered'
                )

    def get_transaction_number(self, obj):
        return ''

    def get_tendered(self, obj):
        return 0.00

    def get_payment_name(self, obj):
        try:
            return obj.name
        except:
            return ''
