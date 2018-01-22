from django.utils.formats import localize
import logging
import  random
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
            ProductVariant
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
    item = JSONField() #ItemSerializer(many=True)
    history = JSONField() #HistorySerializer(many=True)

    class Meta:
        model = Table
        fields = (
                 'id',
                 'user',
                 'supplier',
                 'quantity',
                 'total_net',
                 'amount_paid',
                 'balance',
                 'item',
                 'history'
                )

    def create(self, validated_data):
        # new purchase instance
        # Table.objects.all().delete()
        instance = Table()
        # generate invoice number from last id
        try:
            invoice_number = Table.objects.latest('id').id
            print '*'*120
            print(invoice_number.invoice_number)
        except:
            invoice_number = 1
        invoice_number = 'INV/'+str(invoice_number)+str(random.randint(2, 10))

        instance.supplier = validated_data.get('supplier')
        instance.invoice_number = invoice_number
        instance.total_net = validated_data.get('total_net')
        instance.sub_total = validated_data.get('sub_total')
        instance.quantity = validated_data.get('quantity')
        instance.balance = validated_data.get('balance')
        instance.amount_paid = validated_data.get('amount_paid')
        instance.payment_data = validated_data.get('payment_data')
        instance.history = validated_data['history']
        instance.item = validated_data['item']
        instance.save()

        # create history
        # try:
        #histories = json.loads(validated_data.pop('purchase_history'))
        histories = validated_data['history']
        for item in histories:
            # create history
            history = HistoryEntry()
            history.purchase = instance
            history.tendered = item['tendered']
            history.payment_name = item['payment_name']
            history.transaction_number = item['transaction_number']
            history.save()
        # except Exception as e:
        #     raise ValidationError(e)
        # add stock & quantity
        try:
            items = validated_data['item']
        except Exception as e:
            raise ValidationError(e)
        for item in items:
            # create purchased items
            single_item = Item()
            single_item.purchase = instance
            single_item.total_cost = item['total_cost']
            single_item.unit_cost = item['cost_price']
            single_item.product_name = item['product_name']
            single_item.sku = item['sku']
            single_item.quantity = item['qty']
            single_item.order = 1
            single_item.save()

            # Item.objects.create(purchase=instance, **item)
            try:
                stock = Stock.objects.get(variant__sku=item['sku'])
                Stock.objects.increase_stock(stock, item['qty'])
            except Exception as e:
                # create new stock
                stock = Stock()
                stock.variant = ProductVariant.objects.get(sku=item['sku'])
                stock.quantity = item['qty']
                stock.cost_price = item['cost_price']
                stock.save()

                error_logger.error(e)
        return instance


class TableListSerializer(serializers.ModelSerializer):
    single_url = HyperlinkedIdentityField(view_name='dashboard:purchase-variant-single')
    detail_url = HyperlinkedIdentityField(view_name='dashboard:purchase-variant-detail')
    purchased_item = ItemSerializer(many=True)
    purchase_history = HistorySerializer(many=True)
    supplier_name = serializers.SerializerMethodField()
    total_purchases = SerializerMethodField()
    total_cost = SerializerMethodField()
    total_quantity = SerializerMethodField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = (
                 'id',
                 'user',
                 'supplier_name',
                 'total_net',
                 'amount_paid',
                 'invoice_number',
                 'balance',
                 'quantity',
                 'total_cost',
                 'total_quantity',
                 'total_purchases',
                 'single_url',
                 'detail_url',
                 'purchased_item',
                 'purchase_history',
                 'date'
                )

    def get_total_quantity(self, obj):
        try:
            return "{:,}".format(Table.objects.total_quantity(obj))
        except:
            return 0

    def get_total_purchases(self, obj):
        try:
            return "{:,}".format(Table.objects.total_purchases(obj))
        except:
            return 0

    def get_total_cost(self, obj):
        try:
            return "{:,}".format(Table.objects.total_cost(obj))
        except:
            return 0

    def get_supplier_name(self, obj):
        try:
            return obj.supplier.name
        except:
            return ''

    def get_date(self, obj):
        return localize(obj.created)
