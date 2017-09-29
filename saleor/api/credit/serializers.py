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
from ...credit.models import Credit, CreditedItem
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
    url = HyperlinkedIdentityField(view_name='product-api:sales-details')
    credititems = ItemsSerializer(many=True)
    cashier = SerializerMethodField()
    class Meta:
        model = Credit
        fields = ('id',
                 'user',
                 'invoice_number',
                 'total_net',
                 'sub_total',                 
                 'url',
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
                )

    def get_cashier(self,obj):
        name = User.objects.get(pk=obj.user.id)
        return name.name


class CreateCreditSerializer(serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='product-api:sales-details')
    credititems = TrackSerializer(many=True)
    class Meta:
        model =  Credit
        fields = ('id',
                 'user',
                 'invoice_number',
                 'total_net',
                 'sub_total',                 
                 'url',
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
                )

    def validate_total_net(self,value):
        data = self.get_initial()        
        try:
            self.total_net = Decimal(data.get('total_net'))
        except:
            raise ValidationError('Total Net should be a decimal/integer')
        return value

    def validate_customer(self,value):
        data = self.get_initial()
        try:
            customer = Customer.objects.get(pk=data.get("customer"))
        except:
            raise ValidationError('Incorrect customer details')
        if customer.creditable:
            print 'creditable'
        else:
            raise ValidationError('Customer is not creditable')
            print 'not creditable'        
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
        try:
           total_net = Decimal(validated_data.get('total_net'))
        except:
           total_net = Decimal(0)
        try:
            if validated_data.get('customer'):
                customer = Customer.objects.get(pk=validated_data.get('customer'))
                if not customer.creditable:
                    raise ValidationError('customer is not creditable')
            else:
                customer = Customer.objects.get(name=validated_data.get('customer_name'))
        except:
            name = validated_data.get('customer_name')
            if validated_data.get('mobile') and validated_data.get('customer_name'):
                mobile = validated_data.get('mobile')
                customer = Customer.objects.create(name=name, mobile=mobile, creditable=True)
            else:
                customer = None
                raise ValidationError('customer details provided dont meet adding customer criteria')

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
                  
        solditems_data = validated_data.pop('credititems')        
        credit = Credit.objects.create(user=validated_data.get('user'),
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
                                     customer_name=validated_data.get('customer_name'))
        for solditem_data in solditems_data:
            CreditedItem.objects.create(credit=credit,**solditem_data)           
            try:
                stock = Stock.objects.get(variant__sku=solditem_data['sku'])
                if stock:                
                    Stock.objects.decrease_stock(stock,solditem_data['quantity'])                
                    print stock.quantity
                else: 
                    print 'stock not found'
            except:
                print 'Error reducing stock!'
            
                
        return credit

class CreditUpdateSerializer(serializers.ModelSerializer):      
    credititems = TrackSerializer(many=True)
    class Meta:
        model = Credit
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
                print 'balance '+str(sale.balance)
                print 'amount '+str(amount_paid)
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
        instance.debt = instance.debt-validated_data.get('amount_paid', instance.amount_paid)
        instance.amount_paid = instance.amount_paid+validated_data.get('amount_paid', instance.amount_paid)
        if instance.amount_paid >= instance.total_net:
            instance.status = 'fully-paid'            
        else:
            instance.status = validated_data.get('status', instance.status)
        instance.mobile = validated_data.get('mobile', instance.mobile)   
        
        instance.customer_name = validated_data.get('customer_name', instance.customer_name)
        instance.save()        
        return instance


