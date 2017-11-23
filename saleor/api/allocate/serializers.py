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
from ...sale.models import (
            Terminal,
            )
from ...allocate.models import Allocate, AllocatedItem
from ...product.models import (
            ProductVariant,
            Stock,
            )
from decimal import Decimal
import logging

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')
User = get_user_model()


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllocatedItem
        fields = (
                'id',
                'order',
                'sku',
                'allocated_quantity',
                'quantity',
                'sold',
                'unsold',
                'unit_cost',
                'total_cost',
                'product_name',
                'product_category',
                'tax',
                'discount',
                 )


class ItemsSerializer(serializers.ModelSerializer):
    available_stock = SerializerMethodField()
    item_pk = SerializerMethodField()

    class Meta:
        model = AllocatedItem
        fields = (
                'id',
                'order',
                'sku',
                'quantity',
                'sold',
                'unsold',
                'allocated_quantity',
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


class AllocateListSerializer(serializers.ModelSerializer):
    update_url = HyperlinkedIdentityField(view_name='allocate-api:update-allocate')
    allocated_items = ItemsSerializer(many=True)
    cashier = SerializerMethodField()

    class Meta:
        model = Allocate
        fields = (
                 'id',
                 'user',
                 'invoice_number',
                 'total_net',
                 'sub_total',                 
                 'update_url',
                 'balance',
                 'terminal',
                 'amount_paid',
                 'agent',
                 'car',
                 'mobile',
                 'customer_name',
                 'cashier',
                 'status',
                 'total_tax',
                 'discount_amount',
                 'due_date',
                 'debt',
                 'allocated_items',
                )

    def get_cashier(self, obj):
        name = User.objects.get(pk=obj.user.id)
        return name.name


class CreateAllocateSerializer(serializers.ModelSerializer):
    update_url = HyperlinkedIdentityField(view_name='allocate-api:update-allocate')
    allocated_items = TrackSerializer(many=True)

    class Meta:
        model = Allocate
        fields = (
                 'id',
                 'user',
                 'invoice_number',
                 'total_net',
                 'sub_total',                 
                 'update_url',
                 'balance',
                 'terminal',
                 'amount_paid',
                 'agent',
                 'car',
                 'mobile',
                 'customer_name',
                 'status',
                 'total_tax',
                 'allocated_items',
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

    def create(self, validated_data):
        try:
           total_net = Decimal(validated_data.get('total_net'))
        except:
           total_net = Decimal(0)
        solditems_data = validated_data.pop('allocated_items')
        credit = Allocate.objects.create(
                                     user=validated_data.get('user'),
                                     invoice_number=validated_data.get('invoice_number'),
                                     total_net=validated_data.get('total_net'),
                                     sub_total=validated_data.get('sub_total'),
                                     balance=validated_data.get('balance'),
                                     terminal=validated_data.get('terminal'),
                                     amount_paid=validated_data.get('amount_paid'),
                                     agent=validated_data.get('agent'),
                                     car=validated_data.get('car'),
                                     status='payment-pending',
                                     mobile=validated_data.get('mobile'),
                                     debt=validated_data.get('total_net'),
                                     customer_name=validated_data.get('customer_name'))
        for solditem_data in solditems_data:
            AllocatedItem.objects.create(allocate=credit, **solditem_data)
            try:
                stock = Stock.objects.get(variant__sku=solditem_data['sku'])
                if stock:                
                    Stock.objects.decrease_stock(stock,solditem_data['allocated_quantity'])
                    print stock.quantity
                else: 
                    print('stock not found')
            except Exception as e:
                error_logger.error(e)
                
        return credit


class AllocateUpdateSerializer(serializers.ModelSerializer):
    allocated_items = TrackSerializer(many=True)

    class Meta:
        model = Allocate
        fields = (
                 'id',
                 'invoice_number',
                 'total_net',
                 'sub_total',                
                 'balance',
                 'terminal',
                 'amount_paid',                 
                 'mobile',
                 'customer_name',
                 'status',
                 'total_tax',
                 'discount_amount',
                 'debt',
                 'allocated_items',
                 )

    def validate_total_net(self, value):
        data = self.get_initial()        
        try:
            total_net = Decimal(data.get('total_net'))
        except:
            raise ValidationError('Total Net should be a decimal/integer')

    def validate_debt(self,value):
        data = self.get_initial()        
        try:
            debt = Decimal(data.get('debt'))
        except:
            raise ValidationError('Debt should be a decimal/integer')
        return value

    def validate_amout_paid(self,value):
        data = self.get_initial()        
        try:
            amount_paid = Decimal(data.get('amount_paid'))
        except:
            raise ValidationError('Amount paid should be a decimal/integer')
        return value

    def update(self, instance, validated_data):
        terminal = Terminal.objects.get(pk=self.terminal_id)
        for x in validated_data.get('allocated_items'):
            old = instance.item_detail(x['sku'])
            old.sold += x['quantity']
            old.quantity = x['quantity']
            old.total_cost = x['total_cost']
            unsold = old.allocated_quantity - old.sold
            old.unsold = unsold
            stock = Stock.objects.get(variant__sku=x['sku'])

            # handle return unsold product to stock
            if validated_data.get('status', instance.status) == 'fully-paid':
                if stock:
                    Stock.objects.increase_stock(stock, unsold)
                    print stock.quantity
                else:
                    print 'stock not found'
            old.save()

        terminal.amount += Decimal(validated_data.get('amount_paid', instance.amount_paid))       
        terminal.save()        
        instance.debt = instance.debt-validated_data.get('amount_paid', instance.amount_paid)
        instance.total_sale += validated_data.get('amount_paid', instance.amount_paid)

        instance.amount_paid = validated_data.get('amount_paid', instance.amount_paid)

        instance.status = validated_data.get('status', instance.status)

        instance.mobile = validated_data.get('mobile', instance.mobile)   
        
        instance.customer_name = validated_data.get('customer_name', instance.customer_name)
        instance.save()        
        return instance


