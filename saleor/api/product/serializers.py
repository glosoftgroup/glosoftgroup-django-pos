from datetime import date
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
from django.db.models import Q, Sum, Count
from ...decorators import user_trail
from ...discount.models import Sale
from ...discount.models import get_variant_discounts
from ...sale.models import (
            Sales, 
            SoldItem,
            Terminal,
            PaymentOption)
from ...product.models import (
            Product,
            ProductVariant,
            ProductAttribute,
            AttributeChoiceValue,
            Stock,
            )
from ...customer.models import Customer
from ...site.models import SiteSettings


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
                'unit_purchase',
                'total_purchase',
                'product_name',
                'product_category',
                'tax',
                'attributes',
                'discount'
                 )


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


class ItemsSerializer(serializers.ModelSerializer):
    available_stock = SerializerMethodField()

    class Meta:
        model = SoldItem
        fields = (
                'order',
                'sku',
                'quantity',
                'unit_cost',
                'unit_purchase',
                'total_purchase',
                'total_cost',
                'product_name',
                'product_category',
                'available_stock',
                'tax',
                'discount',
                 )

    def get_available_stock(self, obj):
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
        fields = (
                 'id',
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
                 'discount_amount'
                )

    def get_cashier(self,obj):
        name = User.objects.get(pk=obj.user.id)
        return name.name


class SalesSerializer(serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='product-api:sales-details')
    solditems = TrackSerializer(many=True)
    payment_data = JSONField()

    class Meta:
        model = Sales
        fields = (
                 'id',
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

    def validate_total_net(self, value):
        data = self.get_initial()        
        try:
            self.total_net = Decimal(data.get('total_net'))
        except:
            raise ValidationError('Total Net should be a decimal/integer')
        return value

    def validate_total_tax(self, value):
        data = self.get_initial()        
        try:
            total_net = Decimal(data.get('total_net'))
            total_tax = Decimal(data.get('total_tax'))
            if total_tax >= total_net:
                raise ValidationError('Total tax cannot be more than total net')
        except:
            raise ValidationError('Total Net should be a decimal/integer')
        return value

    def validate_discount_amount(self, value):
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

    def create(self, validated_data):
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
        sales.user = validated_data.get('user')
        sales.invoice_number = validated_data.get('invoice_number')
        sales.total_net = validated_data.get('total_net')
        sales.sub_total = validated_data.get('sub_total')
        sales.balance = validated_data.get('balance')
        sales.terminal = validated_data.get('terminal')
        sales.amount_paid = validated_data.get('amount_paid')
        sales.status = status
        sales.payment_data = validated_data.get('payment_data')
        sales.total_tax = total_tax
        sales.mobile = validated_data.get('mobile')
        sales.discount_amount = validated_data.get('discount_amount')
        sales.customer_name = validated_data.get('customer_name')
        sales.save()

        # add payment options
        payment_data = validated_data.get('payment_data')        
        for option in payment_data:
            pay_opt = PaymentOption.objects.get(pk=int(option['payment_id']))
            sales.payment_options.add(pay_opt)
            if pay_opt.name == "Loyalty Points":
                points_eq = SiteSettings.objects.get(pk=1).loyalty_point_equiv
                if points_eq == 0:
                    loyalty_points = 0
                else:
                    loyalty_points = Decimal(option['value']) * Decimal(points_eq)
                    Customer.objects.redeem_points(customer, trunc(loyalty_points))
            else:
                points_eq = pay_opt.loyalty_point_equiv
                if points_eq == 0:
                    loyalty_points = 0
                else:
                    loyalty_points = Decimal(option['value'])/Decimal(points_eq)
                try:
                    if trunc(loyalty_points) >= 0:
                        Customer.objects.gain_points(customer, trunc(loyalty_points))
                except Exception as e:
                    error_logger.error(e)

        for solditem_data in solditems_data:
            item_temp = SoldItem.objects.create(sales=sales, **solditem_data)
            item = item_temp
            item_temp.delete()
            carry = int(solditem_data['quantity'])
            checker = True
            # try:
            while checker:
                stock = Stock.objects.filter(variant__sku=solditem_data['sku']).first()
                if stock:
                    item.id = None
                    if stock.quantity > 0:
                        if carry >= stock.quantity:
                            try:
                                item.unit_purchase = stock.cost_price.gross
                            except:
                                pass
                            try:
                                item.total_purchase = stock.cost_price.gross * Decimal(stock.quantity)
                            except:
                                pass
                            item.stock_id = stock.pk
                            item.quantity = stock.quantity
                            item.minimum_price = stock.minimum_price.gross
                            item.wholesale_override = stock.wholesale_override.gross
                            item.low_stock_threshold = stock.low_stock_threshold
                            item.unit_cost = stock.price_override.gross
                            item.total_cost = stock.price_override.gross * stock.quantity
                            item.save()
                            carry -= stock.quantity
                            stock.delete()
                            if carry <= 0:
                                checker = False
                        else:
                            # Stock.objects.decrease_stock(stock, carry)
                            stock.quantity -= carry
                            stock.save()
                            try:
                                item.unit_purchase = stock.cost_price.gross
                            except:
                                pass
                            try:
                                item.total_purchase = stock.cost_price.gross * Decimal(carry)
                            except:
                                pass
                            item.stock_id = stock.pk
                            item.quantity = carry
                            item.minimum_price = stock.minimum_price.gross
                            item.wholesale_override = stock.wholesale_override.gross
                            item.low_stock_threshold = stock.low_stock_threshold
                            item.unit_cost = stock.price_override.gross
                            item.total_cost = stock.price_override.gross * carry

                            item.save()

                            checker = False
                    else:
                        stock.delete()
                        checker = False
                else:
                    print('stock not found')
                    checker = False

            # except Exception as e:
            #     print('Error reducing stock!')
            #     print e
            #     error_logger.error(e)
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

    def get_item_price(self, obj):
        item_price = obj.price.gross
        return item_price


class ProductStockListSerializer(serializers.ModelSerializer):    
    productName = SerializerMethodField()
    price = SerializerMethodField()
    cost_price = SerializerMethodField()
    quantity = SerializerMethodField()
    tax = SerializerMethodField()
    discount = SerializerMethodField()
    product_category = SerializerMethodField()
    min_price = SerializerMethodField()
    wholesale_price = SerializerMethodField()
    attributes_list = SerializerMethodField()
    stock = StockSerializer(many=True)

    class Meta:        
        model = ProductVariant
        fields = (
            'id',
            'productName',
            'sku',
            'price',
            'cost_price',
            'wholesale_price',
            'min_price',
            'tax',
            'discount',
            'quantity',
            'product_category',
            'attributes_list',
            'stock'
            )

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
                discount = (Decimal(discount)*Decimal(price))
            except:
                discount = discount.amount.gross      

        return discount

    def get_quantity(self, obj):
        quantity = obj.get_stock_quantity()
        return quantity

    def get_productName(self, obj):
        product_name = obj.display_product()
        return product_name

    def get_min_price(self, obj):
        try:
            return obj.get_min_price_per_item().gross
        except Exception as e:
            return 0

    def get_cost_price(self, obj):
        return obj.get_stock_cost_price()

    def get_wholesale_price(self, obj):
        try:
            return obj.get_wholesale_price_per_item().gross
        except Exception as e:
            return 0

    def get_price(self, obj):
        try:
            price = obj.get_price_per_item().gross
            return price
        except Exception as e:
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


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant


class UserSerializer(serializers.ModelSerializer):
    # used during jwt authentication
    permissions = SerializerMethodField()

    class Meta:
        model = User
        fields = ['id','email','name','permissions']

    def get_permissions(self, obj):
        info_logger.info('User: '+str(obj.name)+' '+str(obj.email)+' logged in via api')
        user_trail(obj.name, 'logged in via api','view')
        
        permissions = []
        if obj.has_perm('sales.make_sale'):
            permissions.append('make_sale') 
        if obj.has_perm('sales.make_invoice'):
            permissions.append('make_invoice')
        if obj.has_perm('sales.credit_sale'):
            permissions.append('credit_sale')
        if obj.has_perm('sales.credit_receive'):
            permissions.append('credit_receive')
        if obj.has_perm('product.change_product'):
            permissions.append('change_product')
        return permissions
