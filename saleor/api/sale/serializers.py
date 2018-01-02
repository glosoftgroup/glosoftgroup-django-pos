from rest_framework import serializers
from django.contrib.auth import get_user_model

from ...sale.models import Sales as Table
from ...sale.models import SoldItem as Item

User = get_user_model()


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = (
                'id',
                'sku',
                'quantity',
                'unit_cost',
                'total_cost',
                'product_name',
                'product_category',
                'tax',
                'discount'
                 )


class ListSerializer(serializers.ModelSerializer):
    solditems = ItemSerializer(many=True)

    class Meta:
        model = Table
        fields = ('id',
                  'user',
                  'invoice_number',
                  'created',
                  'total_net',
                  'sub_total',
                  'balance',
                  'terminal',
                  'amount_paid',
                  'solditems',
                  'customer',
                  'mobile',
                  'customer_name',
                  'payment_data',
                  'status',
                  'total_tax',
                  'discount_amount'
                  )


