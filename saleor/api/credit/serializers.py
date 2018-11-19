from django.utils.formats import localize
from rest_framework.serializers import (
    HyperlinkedIdentityField,
    JSONField,
    SerializerMethodField,
    ValidationError
)
from rest_framework.exceptions import ParseError

from rest_framework import serializers
from django.contrib.auth import get_user_model

from ...sale.models import Terminal, PaymentOption
from ...credit.models import (
    Credit,
    CreditedItem,
    CreditHistoryEntry
)
from ...product.models import (
    ProductVariant,
    Stock,
)
from decimal import Decimal
from ...customer.models import Customer
from .utilities import clear_old_debts_using_change
from saleor.countertransfer.models import CounterTransferItems

from structlog import get_logger

logger = get_logger(__name__)
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
            'attributes',
            'transfer_id',
            'stock_id',
            'counter'
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
            'attributes',
        )

    def get_item_pk(self, obj):
        return obj.pk

    def get_available_stock(self, obj):
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
            'debt'
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
            'debt'
        )

    def validate_total_net(self, value):
        data = self.get_initial()
        try:
            self.total_net = Decimal(data.get('total_net'))
        except:
            logger.error('Total Net should be a decimal/integer')
            raise ValidationError('Total Net should be a decimal/integer')
        return value

    def validate_customer(self, value):
        data = self.get_initial()
        try:
            customer = Customer.objects.get(pk=data.get("customer"))
        except:
            logger.error('Incorrect customer details')
            raise ValidationError('Incorrect customer details')
        if customer.creditable:
            print 'creditable'
        else:
            logger.error("Customer is not creditable")
            raise ValidationError('Customer is not creditable')
        return value

    def validate_mobile(self, value):
        data = self.get_initial()
        try:
            customer = Customer.objects.get(mobile=data.get("mobile"))
            if customer.creditable:
                pass
            else:
                logger.error('Customer is not creditable: code 400')
                raise ParseError('Customer is not creditable', code=400)
        except Exception as e:
            logger.error(e)
        return value

    def validate_terminal(self, value):
        data = self.get_initial()
        self.terminal_id = int(data.get('terminal'))
        self.l = []
        terminals = Terminal.objects.all()
        for term in terminals:
            self.l.append(term.pk)
        if not self.terminal_id in self.l:
            logger.error('Terminal specified does not exist')
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
            logger.error('customer details provided do not meet adding customer criteria')
            raise ParseError('customer details provided do not meet adding customer criteria')

        customer = Customer.objects.filter(**kwargs)
        if customer.exists():
            if not customer.get().creditable:
                logger.error('Customer ' + kwargs['name'] + ' is not creditable')
                raise ParseError('Customer ' + kwargs['name'] + ' is not creditable', code=400)

        if not customer.exists():
            kwargs['creditable'] = True
            customer = Customer.objects.create(**kwargs)
        else:
            customer = customer.first()

        solditems_data = validated_data.pop('credititems')
        credit = Credit()
        credit.user = validated_data.get('user')
        credit.invoice_number = validated_data.get('invoice_number')
        credit.total_net = validated_data.get('total_net')
        credit.sub_total = validated_data.get('sub_total')
        credit.balance = validated_data.get('balance')
        credit.terminal = validated_data.get('terminal')
        credit.amount_paid = validated_data.get('amount_paid')
        credit.customer = customer
        credit.status = 'payment-pending'
        credit.mobile = validated_data.get('mobile')
        credit.debt = validated_data.get('debt')
        credit.due_date = validated_data.get('due_date')
        credit.customer_name = validated_data.get('customer_name')
        credit.save()
        # add credit history
        try:
            history = CreditHistoryEntry()
            history.credit = credit
            history.balance = validated_data.get('total_net')
            history.amount = validated_data.get('amount_paid')
            history.save()
        except Exception as e:
            logger.error(e)

        for solditem_data in solditems_data:
            try:
                item_temp = CreditedItem.objects.create(credit=credit, **solditem_data)
                item = item_temp
                item_temp.delete()
            except Exception as ex:
                logger.error('error create credit items', exception=ex)

            # reduce stock based on the existence of shop or not
            if solditem_data.get('counter'):
                logger.info('reduce stock for shop ', shop_available=True, shop_id=solditem_data.get('counter'))
                # if shop is found then reduce from CounterTransferItems
                try:
                    stock_item = CounterTransferItems.objects.get(pk=solditem_data['transfer_id'])
                    if stock_item:
                        CounterTransferItems.objects.decrease_stock(stock_item, solditem_data['quantity'])
                    else:
                        logger.info('stock item not found in shop', shop_available=True, shop_id=solditem_data.get('counter'), item_id=solditem_data['transfer_id'])
                except Exception as ex:
                    logger.error('Error reducting shop stock', exception=ex, shop_available=True)

                if item:
                    item.save()
            else:
                # reduce from the main stock
                logger.info('no shop details', shop_available=False)

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
                                item.quantity = stock.quantity
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
                                item.quantity = carry
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

        return credit


class CreditUpdateSerializer(serializers.ModelSerializer):
    credititems = TrackSerializer(many=True)
    payment_data = JSONField()
    apply_to_pending = serializers.BooleanField(write_only=True)

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
            'payment_data',
            'apply_to_pending',
        )

    def validate_status(self, value):
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
                logger.error("Status error. Amount paid is less than balance.")
                raise ValidationError("Status error. Amount paid is less than balance.")
            else:
                return value
        else:
            logger.error('Enter correct Status. Expecting either fully-paid/payment-pending')
            raise ValidationError('Enter correct Status. Expecting either fully-paid/payment-pending')

    def validate_total_net(self, value):
        data = self.get_initial()
        try:
            total_net = Decimal(data.get('total_net'))
        except:
            logger.error('Total Net should be a decimal/integer')
            raise ValidationError('Total Net should be a decimal/integer')

    def validate_debt(self, value):
        data = self.get_initial()
        try:
            debt = Decimal(data.get('debt'))
        except:
            raise ValidationError('Debt should be a decimal/integer')
        return value

    def validate_balance(self, value):
        data = self.get_initial()
        try:
            balance = Decimal(data.get('balance'))
        except:
            raise ValidationError('Debt should be a decimal/integer')
        return value

    def validate_amout_paid(self, value):
        data = self.get_initial()
        try:
            amount_paid = Decimal(data.get('amount_paid'))
        except:
            raise ValidationError('Amount paid should be a decimal/integer')
        return value

    def validate_terminal(self, value):
        data = self.get_initial()
        self.terminal_id = int(data.get('terminal'))
        # try:
        terminal = Terminal.objects.filter(pk=self.terminal_id)
        if terminal:
            return value
        else:
            raise ValidationError('Terminal specified does not exist')
        # except:
        #     raise ValidationError('Terminal specified does not exist')

    def validate_payment_data(self, value):
        data = self.get_initial()
        dictionary_value = dict(data.get('payment_data'))
        return value

    def update(self, instance, validated_data):
        terminal = Terminal.objects.get(pk=self.terminal_id)

        terminal.amount += Decimal(validated_data.get('amount_paid', instance.amount_paid))
        terminal.save()
        instance.debt = instance.debt - validated_data.get('amount_paid', instance.amount_paid)
        instance.amount_paid = instance.amount_paid + validated_data.get('amount_paid', instance.amount_paid)
        instance.payment_data = validated_data.get('payment_data')

        if instance.amount_paid >= instance.total_net:
            instance.status = 'fully-paid'
            instance.amount_paid = instance.total_net
            instance.debt = 0

            payment_data = validated_data.get('payment_data')
            for option in payment_data:
                pay_opt = PaymentOption.objects.get(pk=int(option['payment_id']))
                instance.payment_options.add(pay_opt)

        else:
            instance.status = validated_data.get('status', instance.status)
        instance.mobile = validated_data.get('mobile', instance.mobile)

        instance.customer_name = validated_data.get('customer_name', instance.customer_name)
        instance.save()

        if validated_data.get('apply_to_pending'):

            logger.info('clearing old debts')

            """ handle the balance as a positive """
            change = validated_data.get('balance')
            if change < 0:
                change = change * -1
            clear_old_debts_using_change(change, instance)

        # add credit history
        try:
            history = CreditHistoryEntry()
            history.credit = instance
            history.amount = Decimal(validated_data.get('amount_paid'))
            history.balance = instance.total_net - instance.amount_paid
            history.save()
        except Exception as e:
            logger.error(e)
        return instance


class TableListSerializer(serializers.ModelSerializer):
    detail_url = HyperlinkedIdentityField(view_name='dashboard:credit-detail2')
    date = SerializerMethodField()
    due_date = SerializerMethodField()
    customer_name = SerializerMethodField()
    customer_mobile = SerializerMethodField()
    credit_status = SerializerMethodField()
    is_due = SerializerMethodField()
    credit_amount = SerializerMethodField()

    class Meta:
        model = Credit
        fields = (
            'id',
            'invoice_number',
            'status',
            'is_due',
            'customer_name',
            'customer_mobile',
            'credit_status',
            'credit_amount',
            'amount_paid',
            'debt',
            'detail_url',
            'due_date',
            'date',
            'balance'
        )

    def get_is_due(self, obj):
        if obj.is_fully_paid:
            return '<span class ="text-success  icon-checkmark-circle"> <i> </i> </span>'
        else:
            return '<span class ="badge badge-flat border-warning text-warning-600" > Pending..</span>'

    def get_credit_amount(self, obj):
        try:
            return "{:,}".format(obj.total_net)
        except:
            return 0

    def get_credit_status(self, obj):
        if obj.status == 'payment-pending':
            return '<span class="badge badge-flat border-warning text-warning-600" > Pending..</span>'
        return '<span class ="text-success  icon-checkmark-circle" > <i> </i> </span>'

    def get_date(self, obj):
        return localize(obj.created)

    def get_due_date(self, obj):
        return localize(obj.due_date)

    def get_customer_name(self, obj):
        return obj.customer.name

    def get_customer_mobile(self, obj):
        return obj.customer.mobile


class DistinctTableListSerializer(serializers.ModelSerializer):
    single_url = HyperlinkedIdentityField(view_name='dashboard:single-credit-list')
    date = SerializerMethodField()
    customer_name = SerializerMethodField()
    customer_mobile = SerializerMethodField()
    total_due = SerializerMethodField()

    class Meta:
        model = Credit
        fields = (
            'id',
            'customer_name',
            'customer_mobile',
            'total_due',
            'sub_total',
            'balance',
            'terminal',
            'amount_paid',
            'single_url',
            'date',
        )

    def get_date(self, obj):
        return localize(obj.created)

    def get_total_due(self, obj):
        return Credit.objects.customer_credits(obj.customer)

    def get_customer_name(self, obj):
        return obj.customer.name

    def get_customer_mobile(self, obj):
        return obj.customer.mobile


