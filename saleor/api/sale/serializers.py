from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum, Count

from ...sale.models import Sales as Table
from ...sale.models import SoldItem as Item

User = get_user_model()


class ItemListSerializer(serializers.ModelSerializer):
    summary = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ('id', 'summary')

    def get_summary(self, obj):
        summary = Item.objects.values('product_name', 'product_category').annotate(
            c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
            '-quantity__sum')
        return summary


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
