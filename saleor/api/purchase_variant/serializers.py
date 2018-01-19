from decimal import Decimal
from math import trunc
import logging
from rest_framework.serializers import (
                ModelSerializer,
                HyperlinkedIdentityField,
                SerializerMethodField,
                ValidationError,
                JSONField
                )
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...purchase.models import PurchaseVariant as Table
from saleor.purchase.models import PurchasedItem as Item
from saleor.purchase.models import PurchaseVariantHistoryEntry as HistoryEntry
from ...product.models import (
            Stock,
            )


User = get_user_model()

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = (
                'order',
                'sku',
                'quantity',
                'unit_cost',
                'total_cost',
                'unit_purchase',
                'total_purchase',
                'product_name',
                 )


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryEntry
        fields = (
                'tendered',
                'balance',
                'payment_name',
                'transaction_number'
                 )


class TableCreateSerializer(serializers.ModelSerializer):
    purchased_item = ItemSerializer(many=True)
    purchase_history = HistorySerializer(many=True)

    class Meta:
        model = Table
        fields = (
                 'id',
                 'user',
                 'invoice_number',
                 'total_net',
                 'sub_total',
                 'balance',
                 'amount_paid',
                 'purchased_item',
                 'purchase_history'
                )

    def create(self, validated_data):
        # new purchase instance
        instance = Table()
        # generate invoice number
        try:
            invoice_number = Table.objects.latest('id').id
        except:
            invoice_number = 1
        invoice_number = 'INV/'+invoice_number
        try:
            items = validated_data.pop('purchased_item')
        except:
            raise ValidationError('purchased_item field should not be empty')

        instance.invoice_number = invoice_number
        instance.total_net = validated_data.get('total_net')
        instance.sub_total = validated_data.get('sub_total')
        instance.balance = validated_data.get('balance')
        instance.amount_paid = validated_data.get('amount_paid')
        instance.payment_data = validated_data.get('payment_data')
        instance.save()

        # add stock & quantity
        for item in items:
            Item.objects.create(purchase=instance, **item)
            try:
                stock = Stock.objects.get(variant__sku=item['sku'])
                if stock:                
                    Stock.objects.increase_stock(stock,item['quantity'])
                else: 
                    print('stock not found')
            except Exception as e:
                print('Error reducing stock!')
                error_logger.error(e)
        return instance
