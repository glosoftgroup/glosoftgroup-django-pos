from django.conf import settings
from datetime import date
from rest_framework.serializers import (
                ModelSerializer,
                HyperlinkedIdentityField,
                SerializerMethodField,
                ValidationError,
                JSONField
                )

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...decorators import user_trail
import logging
from ...discount.models import Sale
from ...discount.models import get_variant_discounts
from ...sale.models import (
            Sales, 
            SoldItem,
            Terminal,
            PaymentOption)
from ...site.models import SiteSettings
from ...product.models import (
            Product,
            ProductVariant,
            Stock,
            )
from decimal import Decimal
import json
from ...customer.models import Customer


User = get_user_model()

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


class CreateStockSerializer(ModelSerializer):
    class Meta:
         model = Stock
         exclude = ['quantity_allocated']


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoldItem
        fields = (
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
    class Meta:
        model = SoldItem
        fields = (
                'order',
                'sku',
                'quantity',
                'unit_cost',
                'total_cost',
                'product_name',
                'product_category',
                'available_stock',
                'tax',
                'discount',
                 )
    def get_available_stock(self,obj):
        try:
            stock = ProductVariant.objects.get(sku=obj.sku)
            return stock.get_stock_quantity()
        except:
            return 0


class SalesListSerializer(serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='product-api:sales-details')
    solditems = ItemsSerializer(many=True)
    cashier = SerializerMethodField()
    class Meta:
        model = Sales
        fields = ('id',
                 'user',
                 'invoice_number',
                 'total_net',
                 'sub_total',                 
                 'url',
                 'balance',
                 'terminal',
                 'amount_paid',
                 'solditems',
                 'customer',
                 'mobile',
                 'customer_name',
                 'cashier',
                 'payment_options',
                 'status',
                 'total_tax',
                 'discount_amount',
                )

    def get_cashier(self,obj):
        name = User.objects.get(pk=obj.user.id)
        return name.name


class SalesUpdateSerializer(serializers.ModelSerializer):    
    #solditems = ItemsSerializer(required=False,many=True)    
    class Meta:
        model = Sales
        fields = ('id',                 
                 'invoice_number',
                 'total_net',
                 'sub_total',                
                 'balance',
                 'terminal',
                 'amount_paid',                 
                 'mobile',
                 'customer_name',
                 'status',
                 #'solditems',
                 )       
    
    def validate_status(self,value):        
        data = self.get_initial()
        status = str(data.get('status'))        
        if status == 'fully-paid' or status == 'payment-pending':
            status = status 
            invoice_number = data.get('invoice_number')      
            amount_paid = Decimal(data.get('amount_paid'))
            total_net = Decimal(data.get('total_net'))
            balance = Decimal(data.get('balance'))
            sale = Sales.objects.get(invoice_number=invoice_number)
            
            if status == 'fully-paid' and sale.balance > amount_paid:                
                raise ValidationError("Status error. Amount paid is less than balance.")        
            else:
                return value
        else:
            raise ValidationError('Enter correct Status. Expecting either fully-paid/payment-pending')        

    def validate_total_net(self,value):
        data = self.get_initial()        
        try:
            total_net = Decimal(data.get('total_net'))
        except:
            raise ValidationError('Total Net should be a decimal/integer')

    def validate_balance(self,value):
        data = self.get_initial()        
        try:
            balance = Decimal(data.get('balance'))
        except:
            raise ValidationError('Balance should be a decimal/integer')
        return value

    def validate_amout_paid(self,value):
        data = self.get_initial()        
        try:
            amount_paid = Decimal(data.get('amount_paid'))
        except:
            raise ValidationError('Amount paid should be a decimal/integer')
        return value

    def validate_terminal(self,value):
        data = self.get_initial()
        self.terminal_id = int(data.get('terminal'))
        #try:
        terminal = Terminal.objects.filter(pk=self.terminal_id)
        if terminal:
            return value
        else:
            raise ValidationError('Terminal specified does not exist')
        # except:
        #     raise ValidationError('Terminal specified does not exist')
        

    def update(self, instance, validated_data):
        terminal = Terminal.objects.get(pk=self.terminal_id)    

        terminal.amount += Decimal(validated_data.get('amount_paid', instance.amount_paid))       
        terminal.save()        
        instance.balance = instance.balance-validated_data.get('amount_paid', instance.amount_paid)
        instance.amount_paid = instance.amount_paid+validated_data.get('amount_paid', instance.amount_paid)
        if instance.amount_paid >= instance.total_net:
            instance.status = 'fully-paid'
        else:
            instance.status = validated_data.get('status', instance.status)
        instance.mobile = validated_data.get('mobile', instance.mobile)
        
        
        instance.customer_name = validated_data.get('customer_name', instance.customer_name)
        instance.save()        
        return instance


class SalesSerializer(serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='product-api:sales-details')
    solditems = TrackSerializer(many=True)
    payment_data = JSONField()
    class Meta:
        model = Sales
        fields = ('id',
                 'user',
                 'invoice_number',
                 'total_net',
                 'sub_total',                 
                 'url',
                 'balance',
                 'terminal',
                 'amount_paid',
                 'solditems',
                 'customer',
                 'mobile',
                 'customer_name',
                 'status',                
                 'payment_data',
                 'total_tax',
                 'discount_amount'
                )

    def validate_total_net(self,value):
        data = self.get_initial()        
        try:
            self.total_net = Decimal(data.get('total_net'))
        except:
            raise ValidationError('Total Net should be a decimal/integer')
        return value

    def validate_total_tax(self,value):
        data = self.get_initial()        
        try:
            total_net = Decimal(data.get('total_net'))
            total_tax = Decimal(data.get('total_tax'))
            if total_tax >= total_net:
                raise ValidationError('Total tax cannot be more than total net')
        except:
            raise ValidationError('Total Net should be a decimal/integer')
        return value

    def validate_discount_amount(self,value):
        data = self.get_initial()        
        try:
            discount = Decimal(data.get('discount_amount'))            
        except:
            raise ValidationError('Discount should be a decimal/integer *'+str(discount)+'*')
        return value

    def validate_payment_data(self,value):
        data = self.get_initial()
        dictionary_value = dict(data.get('payment_data'))
        return value
    def validate_status(self,value):
        data = self.get_initial()
        status = str(data.get('status'))        
        if status == 'fully-paid' or status == 'payment-pending':
            return value
        else:
            raise ValidationError('Enter correct Status. Expecting either fully-paid/payment-pending')
        
        
    def validate_terminal(self,value):
        data = self.get_initial()
        terminal_id = int(data.get('terminal'))        
        try:
            terminals = Terminal.objects.get(pk=terminal_id)
        except:      
            raise ValidationError('Terminal specified does not exist')
        return value    

    def create(self,validated_data):
        # add sold amount to drawer 
        try:
           total_net = Decimal(validated_data.get('total_net'))
        except:
           total_net = Decimal(0)
        try:
            total_tax = Decimal(validated_data.get('total_tax'))
        except:
            total_tax = Decimal(0)
        terminal = validated_data.get('terminal')               
        terminal.amount += Decimal(total_net)  
        terminal.save()

        sales = Sales() 

        try:
            if validated_data.get('customer'):
                customer = Customer.objects.get(name=validated_data.get('customer'))
            else:
                customer = Customer.objects.get(name=validated_data.get('customer_name'))
            sales.customer = customer
        except:
            name = validated_data.get('customer_name')
            if validated_data.get('mobile'):
                mobile = validated_data.get('mobile')
                customer = Customer.objects.create(name=name, mobile=mobile)
                sales.customer = customer
            else:
                pass
                
        invoice_number = validated_data.get('invoice_number')
        
        try:       
            solditems_data = validated_data.pop('solditems')
        except:
            raise ValidationError('Solditems field should not be empty')
        status = validated_data.get('status')
        # make a sale 
        sales.user=validated_data.get('user')
        sales.invoice_number=validated_data.get('invoice_number')      
        sales.total_net=validated_data.get('total_net')
        sales.sub_total=validated_data.get('sub_total')
        sales.balance=validated_data.get('balance')
        sales.terminal=validated_data.get('terminal')
        sales.amount_paid=validated_data.get('amount_paid')        
        sales.status=status
        sales.payment_data=validated_data.get('payment_data')
        sales.total_tax=total_tax
        sales.mobile=validated_data.get('mobile')
        sales.discount_amount=validated_data.get('discount_amount')
        sales.customer_name=validated_data.get('customer_name')
        sales.save()
        # add payment options
        payment_data = validated_data.get('payment_data')        
        for option in payment_data:
            pay_opt = PaymentOption.objects.get(pk=int(option['payment_id']))
            sales.payment_options.add(pay_opt)
            points_eq = pay_opt.loyalty_point_equiv
            if points_eq == 0:
                loyalty_points = 0
            else:
                loyalty_points = int(option['value'])/points_eq
            try:
                Customer.objects.gain_points(customer,loyalty_points)
            except:
                print 'customer details provided dont meet adding customer criteria'

        for solditem_data in solditems_data:
            SoldItem.objects.create(sales=sales,**solditem_data)
            try:
                stock = Stock.objects.get(variant__sku=solditem_data['sku'])
                if stock:                
                    Stock.objects.decrease_stock(stock,solditem_data['quantity'])                                    
                else: 
                    print 'stock not found'
            except:
                print 'Error reducing stock!'
                
        return sales
        

class OrderedItemSerializer(serializers.Serializer):
    quantity = serializers.CharField()
    sku = serializers.CharField()


class ProductListSerializer(serializers.ModelSerializer):    
    vat_tax = SerializerMethodField()
    item_price = SerializerMethodField()    
    class Meta:
        model = Product
        fields = (
            'id', 
            'name',
            'vat_tax',
            'item_price',
            'description',
           )
    def get_vat_tax(self, obj):
        if obj.product_tax:
            tax = obj.product_tax.tax
        else:
            tax = 0
        return tax
    def get_item_price(self,obj):
        item_price = obj.price.gross
        return item_price


class ProductStockListSerializer(serializers.ModelSerializer):    
    productName = SerializerMethodField()
    price = SerializerMethodField()
    quantity = SerializerMethodField()
    tax = SerializerMethodField()
    discount = SerializerMethodField()
    product_category = SerializerMethodField()
    #description = SerializerMethodField()
    class Meta:        
        model = ProductVariant
        fields = (
            'id',
            'productName',
            'sku',
            'price',
            'tax',
            'discount',
            'quantity',
            'product_category',            
            )

    def get_discount(self,obj):
        today = date.today()
        price = obj.get_price_per_item().gross      
        discounts = Sale.objects.filter(start_date__lte=today).filter(end_date__gte=today)
        discount  = 0
        discount_list = get_variant_discounts(obj, discounts)
        for discount in discount_list:
            try:
                discount = discount.factor
                discount = (Decimal(discount)*Decimal(price))
            except:
                discount = discount.amount.gross      

        return discount

    def get_quantity(self,obj):
        quantity = obj.get_stock_quantity()
        return quantity
    def get_productName(self,obj):
        productName = obj.display_product()
        return productName
    # def get_description(self,obj):
    #     return self.products.description
    def get_price(self,obj):
        price = obj.get_price_per_item().gross
        return price
    def get_tax(self,obj):
        if obj.product.product_tax:
            tax = obj.product.product_tax.tax
        else:
            tax = 0        
        return tax

    def get_product_category(self,obj):
        product_category = obj.product_category()
        return product_category


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant


class UserSerializer(serializers.ModelSerializer):
    # used during jwt authentication
    permissions = SerializerMethodField()
    class Meta:
        model = User
        fields = ['id','email','name','permissions']
    def get_permissions(self,obj):
        info_logger.info('User: '+str(obj.name)+' '+str(obj.email)+' logged in via api')
        user_trail(obj.name, 'logged in via api','view')
        
        permissions = []
        if obj.has_perm('sales.make_sale'):
            permissions.append('make_sale') 
        if obj.has_perm('sales.make_invoice'):
            permissions.append('make_invoice')           
        return permissions