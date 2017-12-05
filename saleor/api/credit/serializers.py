from rest_framework.serializers import (
                ModelSerializer,
                HyperlinkedIdentityField,
                SerializerMethodField,
                ValidationError
                )
from rest_framework.exceptions import ParseError

from rest_framework import serializers
from django.contrib.auth import get_user_model

from ...sale.models import Terminal
from ...credit.models import (
            Credit,
            CreditedItem,
            CreditHistoryEntry
            )
from ...site.models import SiteSettings
from ...product.models import (
            Product,
            ProductVariant,
            Stock,
            )
from decimal import Decimal
from ...customer.models import Customer
import logging
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')
User = get_user_model()


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditedItem
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
                'discount',
                 )


class ItemsSerializer(serializers.ModelSerializer):
    available_stock = SerializerMethodField()
    item_pk = SerializerMethodField()

    class Meta:
        model = CreditedItem
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


class CreditListSerializer(serializers.ModelSerializer):
    update_url = HyperlinkedIdentityField(view_name='credit-api:update-credit')
    credititems = ItemsSerializer(many=True)
    cashier = SerializerMethodField()

    class Meta:
        model = Credit
        fields = (
                 'id',
                 'user',
                 'invoice_number',
                 'created',
                 'total_net',
                 'sub_total',                 
                 'update_url',
                 'balance',
                 'terminal',
                 'amount_paid',
                 'credititems',
                 'customer',
                 'mobile',
                 'customer_name',
                 'cashier',
                 'status',
                 'total_tax',
                 'discount_amount',
                 'due_date',
                 'debt',
                 'car_registration'
                )

    def get_cashier(self, obj):
        name = User.objects.get(pk=obj.user.id)
        return name.name


class CreateCreditSerializer(serializers.ModelSerializer):
    update_url = HyperlinkedIdentityField(view_name='credit-api:update-credit')
    credititems = TrackSerializer(many=True)

    class Meta:
        model = Credit
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
                 'credititems',
                 'customer',
                 'mobile',
                 'customer_name',
                 'status',
                 'total_tax',
                 'discount_amount',
                 'due_date',
                 'debt',
                 'car_registration'
                )

    def validate_total_net(self,value):
        data = self.get_initial()        
        try:
            self.total_net = Decimal(data.get('total_net'))
        except:
            error_logger.error('Total Net should be a decimal/integer')
            raise ValidationError('Total Net should be a decimal/integer')
        return value

    def validate_customer(self, value):
        data = self.get_initial()
        try:
            customer = Customer.objects.get(pk=data.get("customer"))
        except:
            error_logger.error('Incorrect customer details')
            raise ValidationError('Incorrect customer details')
        if customer.creditable:
            print 'creditable'
        else:
            error_logger.error("Customer is not creditable")
            raise ValidationError('Customer is not creditable')
        return value

    def validate_mobile(self, value):
        data = self.get_initial()
        try:
            customer = Customer.objects.get(mobile=data.get("mobile"))
            if customer.creditable:
                pass
            else:
                error_logger.error('Customer is not creditable: code 400')
                raise ParseError('Customer is not creditable', code=400)
        except Exception as e:
            error_logger.error(e)
        return value
        
    def validate_terminal(self, value):
        data = self.get_initial()
        self.terminal_id = int(data.get('terminal'))
        self.l=[]
        terminals = Terminal.objects.all()
        for term in terminals:
            self.l.append(term.pk)
        if not self.terminal_id in self.l:
            error_logger.error('Terminal specified does not exist')
            raise ValidationError('Terminal specified does not exist')
        return value    

    def create(self, validated_data):
        kwargs = {}
        try:
           total_net = Decimal(validated_data.get('total_net'))
        except:
           total_net = Decimal(0)
        # validate customer name and mobile number
        if validated_data.get('mobile') and validated_data.get('customer_name'):
            kwargs['name'] = validated_data.get('customer_name')
            kwargs['mobile'] = validated_data.get('mobile')
        else:
            error_logger.error('customer details provided do not meet adding customer criteria')
            raise ParseError('customer details provided do not meet adding customer criteria')

        customer = Customer.objects.filter(**kwargs)
        if customer.exists():
            if not customer.get().creditable:
                error_logger.error('Customer '+kwargs['name']+' is not creditable')
                raise ParseError('Customer '+kwargs['name']+' is not creditable', code=400)

        if not customer.exists():
            kwargs['creditable'] = True
            customer = Customer.objects.create(**kwargs)
        else:
            customer = customer.first()

        # calculate loyalty_points
        if customer:
            total_net = validated_data.get('total_net')
            points_eq = SiteSettings.objects.get(pk=1)      
            points_eq = points_eq.loyalty_point_equiv
            if points_eq == 0:
                loyalty_points = 0
            else:
                loyalty_points = total_net/points_eq
                  
        solditems_data = validated_data.pop('credititems')        
        credit = Credit.objects.create(
                                     user=validated_data.get('user'),
                                     invoice_number=validated_data.get('invoice_number'),
                                     total_net=validated_data.get('total_net'),
                                     sub_total=validated_data.get('sub_total'),
                                     balance=validated_data.get('balance'),
                                     terminal=validated_data.get('terminal'),
                                     amount_paid=validated_data.get('amount_paid'),
                                     customer=customer,
                                     status='payment-pending',
                                     mobile=validated_data.get('mobile'),
                                     debt=validated_data.get('debt'),
                                     due_date=validated_data.get('due_date'),
                                     customer_name=validated_data.get('customer_name'),
                                     car_registration=validated_data.get('car_registration'))

        # add credit history
        try:
            history = CreditHistoryEntry()
            history.credit = credit
            history.balance = validated_data.get('total_net')
            history.amount = validated_data.get('amount_paid')
            history.save()
        except Exception as e:
            error_logger.error(e)
        for solditem_data in solditems_data:
            try:
                CreditedItem.objects.create(credit=credit, **solditem_data)
                stock = Stock.objects.get(variant__sku=solditem_data['sku'])
                if stock:
                    Stock.objects.decrease_stock(stock, solditem_data['quantity'])
                else:
                    print 'stock not found'
            except Exception as e:
                error_logger.error(e)
        return credit


class CreditUpdateSerializer(serializers.ModelSerializer):      
    credititems = TrackSerializer(many=True)

    class Meta:
        model = Credit
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
                 'credititems',
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
            sale = Credit.objects.get(invoice_number=str(invoice_number))
            if status == 'fully-paid' and sale.balance > amount_paid:
                error_logger.error("Status error. Amount paid is less than balance.")
                raise ValidationError("Status error. Amount paid is less than balance.")
            else:
                return value
        else:
            error_logger.error('Enter correct Status. Expecting either fully-paid/payment-pending')
            raise ValidationError('Enter correct Status. Expecting either fully-paid/payment-pending')        

    def validate_total_net(self, value):
        data = self.get_initial()        
        try:
            total_net = Decimal(data.get('total_net'))
        except:
            error_logger.error('Total Net should be a decimal/integer')
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

    def validate_terminal(self, value):
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
        instance.debt = instance.debt-validated_data.get('amount_paid', instance.amount_paid)
        instance.amount_paid = instance.amount_paid+validated_data.get('amount_paid', instance.amount_paid)
        if instance.amount_paid >= instance.total_net:
            instance.status = 'fully-paid'            
        else:
            instance.status = validated_data.get('status', instance.status)
        instance.mobile = validated_data.get('mobile', instance.mobile)   
        
        instance.customer_name = validated_data.get('customer_name', instance.customer_name)
        instance.save()

        # add credit history
        try:
            history = CreditHistoryEntry()
            history.credit = instance
            history.amount = Decimal(validated_data.get('amount_paid'))
            history.balance = instance.total_net - instance.amount_paid
            history.save()
        except Exception as e:
            error_logger.error(e)
        return instance


