from django.conf import settings
from datetime import date
from rest_framework.serializers import (
                ModelSerializer,
                HyperlinkedIdentityField,
                SerializerMethodField,
                ValidationError,
                )

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...discount.models import Sale
from ...discount.models import get_product_discounts
from ...sale.models import (
            Sales, 
            SoldItem,
            Terminal,
            )
from ...invoice.models import Invoice, InvoicedItem
from ...site.models import SiteSettings
from ...product.models import (
            Product,
            ProductVariant,
            Stock,
            )
from decimal import Decimal
from ...customer.models import Customer


User = get_user_model()


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoicedItem
        fields = (
                'id',
                'order',
                'sku',
                'quantity',
                'unit_cost',
                'total_cost',
                'product_name',
                'product_category',
                'tax',
                'discount'
                 )

class ItemsSerializer(serializers.ModelSerializer):
    available_stock = SerializerMethodField()
    item_pk = SerializerMethodField()
    class Meta:
        model = InvoicedItem
        fields = (
                'id',
                'order',
                'sku',
                'quantity',
                'unit_cost',
                'total_cost',
                'product_name',
                'product_category',
                'available_stock',
                'item_pk',
                'tax',
                'discount',
                 )
    def get_item_pk(self,obj):
        return obj.pk
    def get_available_stock(self,obj):
        try:
            stock = ProductVariant.objects.get(sku=obj.sku)
            return stock.get_stock_quantity()
        except:
            return 0

class InvoiceListSerializer(serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='product-api:sales-details')
    invoiceitems = ItemsSerializer(many=True)
    cashier = SerializerMethodField()

    class Meta:
        model = Invoice
        fields = (
                 'id',
                 'user',
                 'invoice_number',
                 'created',
                 'total_net',
                 'sub_total',                 
                 'url',
                 'balance',
                 'terminal',
                 'amount_paid',
                 'invoiceitems',
                 'customer',
                 'mobile',
                 'customer_name',
                 'cashier',
                 'car_registration'
                )

    def get_cashier(self,obj):
        name = User.objects.get(pk=obj.user.id)
        return name.name




class CreateInvoiceSerializer(serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='product-api:sales-details')
    invoiceitems = TrackSerializer(many=True)
    class Meta:
        model = Invoice
        fields = ('id',
                 'user',
                 'invoice_number',
                 'total_net',
                 'sub_total',                 
                 'url',
                 'balance',
                 'terminal',
                 'amount_paid',
                 'invoiceitems',
                 'customer',
                 'mobile',
                 'customer_name',
                 'status',
                 'car_registration'
                )

    def validate_total_net(self,value):
        data = self.get_initial()        
        try:
            self.total_net = Decimal(data.get('total_net'))
        except:
            raise ValidationError('Total Net should be a decimal/integer')
        return value
        
    def validate_terminal(self,value):
        data = self.get_initial()
        self.terminal_id = int(data.get('terminal'))
        self.l=[]
        terminals = Terminal.objects.all()
        for term in terminals:
            self.l.append(term.pk)
        if not self.terminal_id in self.l:      
            raise ValidationError('Terminal specified does not exist')
        return value    

    def create(self,validated_data):
        # add sold amount to drawer 
        try:
           total_net = Decimal(validated_data.get('total_net'))
        except:
           total_net = Decimal(0)
        try:
            if validated_data.get('customer'):
                customer = Customer.objects.get(name=validated_data.get('customer'))
            else:
                customer = Customer.objects.get(name=validated_data.get('customer_name'))
        except:
            name = validated_data.get('customer_name')
            if validated_data.get('mobile'):
                mobile = validated_data.get('mobile')
                customer = Customer.objects.create(name=name, mobile=mobile)
            else:                
                customer = None
                print 'customer details provided dont meet adding customer criteria'


        invoice_number = validated_data.get('invoice_number')
        # calculate loyalty_points
        if customer:
            total_net = validated_data.get('total_net')
            points_eq = SiteSettings.objects.get(pk=1)      
            points_eq = points_eq.loyalty_point_equiv #settings.LOYALTY_POINT_EQUIVALENCE
            if points_eq == 0:
                loyalty_points = 0
            else:
                loyalty_points = total_net/points_eq
            # customer.loyalty_points += loyalty_points
            # customer.save()
        # get sold products        
        solditems_data = validated_data.pop('invoiceitems')
        # sales = Sales.objects.create(**validated_data)
        sales = Invoice.objects.create(user=validated_data.get('user'),
                                     invoice_number=validated_data.get('invoice_number'),
                                     total_net=validated_data.get('total_net'),
                                     sub_total=validated_data.get('sub_total'),
                                     balance=validated_data.get('balance'),
                                     terminal=validated_data.get('terminal'),
                                     amount_paid=validated_data.get('amount_paid'),
                                     customer=customer,
                                     mobile=validated_data.get('mobile'),
                                     customer_name=validated_data.get('customer_name'),
                                     car_registration=validated_data.get('car_registration'))
        for solditem_data in solditems_data:
            InvoicedItem.objects.create(invoice=sales,**solditem_data)
            
            
                
        return sales

