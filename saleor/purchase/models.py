from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy
from django_prices.models import PriceField
from jsonfield import JSONField

from ..product.models import (
                            Product,
                            ProductVariant,
                            Stock,
                            get_supplier_credit_balance,
                            get_supplier_credit_total
                            )
from ..userprofile.models import Address
from ..customer.models import Customer
from ..supplier.models import Supplier
from saleor.payment.models import PaymentOption

from . import OrderStatus


class PurchaseVariantManager(models.Manager):

    def total_quantity(self, obj, date=None):
        if date:
            allocations = self.get_queryset().filter(
                models.Q(supplier=obj.supplier) &
                models.Q(created__icontains=date)
            )
        else:
            allocations = self.get_queryset().filter(supplier=obj.supplier)
        total = 0
        for item in allocations:
            total += int(item.quantity)
        return total

    def total_purchases(self, obj, date=None):
        if date:
            allocations = self.get_queryset().filter(
                models.Q(supplier=obj.supplier) &
                models.Q(created__icontains=date)
            )
        else:
            allocations = self.get_queryset().filter(supplier=obj.supplier)

        return allocations.count()

    def total_cost(self, obj, date=None):
        if date:
            allocations = self.get_queryset().filter(
                models.Q(supplier=obj.supplier) &
                models.Q(created__icontains=date)
            )
        else:
            allocations = self.get_queryset().filter(supplier=obj.supplier)
        total = 0
        for item in allocations:
            try:
                total += item.total_net
            except Exception as e:
                print(e)
        return total

    def total_credit(self, obj, date=None):
        if date:
            allocations = self.get_queryset().filter(
                models.Q(supplier=obj.supplier) &
                models.Q(created__icontains=date)
            )
        else:
            allocations = self.get_queryset().filter(supplier=obj.supplier)
        total = 0
        for item in allocations:
            try:
                total += item.balance
            except Exception as e:
                print(e)
        return total


@python_2_unicode_compatible
class PurchaseVariant(models.Model):
    status = models.CharField(
        pgettext_lazy('PurchaseOrder field', 'purchase order status'),
        max_length=32, choices=OrderStatus.CHOICES, default=OrderStatus.PENDING)
    quantity = models.IntegerField(
        pgettext_lazy('PurchaseVariant item field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    total_net = models.DecimalField(
        pgettext_lazy('PurchaseVariant field', 'total net'), default=Decimal(0), max_digits=100, decimal_places=2)
    amount_paid = models.DecimalField(
        pgettext_lazy('PurchaseVariant field', 'amount paid'), default=Decimal(0), max_digits=100, decimal_places=2)
    balance = models.DecimalField(
        pgettext_lazy('PurchaseVariant field', 'balance'), default=Decimal(0), max_digits=100, decimal_places=2)
    supplier = models.ForeignKey(
        Supplier, related_name='purchase_variant_supplier', on_delete=models.SET_NULL,
        verbose_name=pgettext_lazy('PurchaseVariant item field', 'supplier'), null=True, blank=True)
    invoice_number = models.CharField(
        pgettext_lazy('PurchaseVariant', 'invoice_number'), null=True, max_length=36,)
    payment_number = models.CharField(
        pgettext_lazy('PurchaseVariant field', 'payment_number'), null=True, max_length=36, )
    payment_options = models.ManyToManyField(
        PaymentOption, related_name='purchase_variant_payment_option', blank=True,
        verbose_name=pgettext_lazy('PurchaseVariant item field',
                                   'payment options'))
    created = models.DateTimeField(
        pgettext_lazy('PurchaseVariant field', 'created'),
        default=now, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        verbose_name=pgettext_lazy('PurchaseVariant history entry field', 'user'))
    comment = models.CharField(
        pgettext_lazy('PurchaseVariant field', 'comment'),
        max_length=100, default='', blank=True)
    item = JSONField(null=True, blank=True)
    history = JSONField(null=True, blank=True)
    objects = PurchaseVariantManager()

    class Meta:
        verbose_name = pgettext_lazy('PurchaseVariant model', 'PurchaseVariant')
        verbose_name_plural = pgettext_lazy('PurchaseVariant model', 'PurchaseVariants')

    def __str__(self):
        return str(self.invoice_number)+' '+str(self.created)

    def get_balance(self):
        try:
            return self.total_cost.gross - self.amount_paid.gross
        except:
            return 0

    def get_total_cost(self):
        if not self.cost_price:
            # return self.cost_price.gross * self.quantity
            # return self.stock.variant.get_price_per_item().gross * self.quantity
            return 0
        return self.cost_price.gross * self.quantity

    def get_cost_price(self):
        if not self.cost_price:
            # return self.stock.cost_price
            return self.stock.variant.get_price_per_item().gross
        return self.cost_price

    def get_supplier_credit_balance(self):
        return get_supplier_credit_balance(self.supplier)

    def get_supplier_credit_total(self):
        return get_supplier_credit_total(self.supplier)


# history
@python_2_unicode_compatible
class PurchaseVariantHistoryEntry(models.Model):
    date = models.DateTimeField(
        pgettext_lazy('Purchase history entry field', 'last history change'),
        default=now, editable=False)
    created = models.DateTimeField(
        pgettext_lazy('Purchase history entry field', 'created'),
        default=now, editable=False)
    purchase = models.ForeignKey(
        PurchaseVariant, related_name='purchase_history',
        verbose_name=pgettext_lazy('Purchase history entry field', 'order'))
    tendered = models.DecimalField(
        pgettext_lazy('Purchase history entry field', 'amount cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    balance = models.DecimalField(
        pgettext_lazy('Purchase history entry field', 'balance'), default=Decimal(0), max_digits=100,
        decimal_places=2)
    transaction_number = models.CharField(
        pgettext_lazy('Purchase history entry field', 'transaction number'),
        max_length=100, default='', blank=True)
    payment_name = models.CharField(
        pgettext_lazy('Purchase history entry field', 'payment option'),
        max_length=100, default='', blank=True)
    comment = models.CharField(
        pgettext_lazy('Purchase history entry field', 'comment'),
        max_length=100, default='', blank=True)
    crud = models.CharField(
        pgettext_lazy('Purchase history entry field', 'crud'),
        max_length=30, default='', blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        verbose_name=pgettext_lazy('Purchase history entry field', 'user'))

    class Meta:
        ordering = ('date',)
        verbose_name = pgettext_lazy(
            'Purchase history entry model', 'Purchase history entry')
        verbose_name_plural = pgettext_lazy(
            'Purchase history entry model', 'Purchase history entries')

    def __str__(self):
        return pgettext_lazy(
            'Purchase history entry str',
            'PurchaseVariantHistoryEntry for terminal #%s') % self.purchase.invoice_number


class PurchaseProductManager(models.Manager):

    def total_quantity(self, obj, date=None):
        if date:
            allocations = self.get_queryset().filter(
                models.Q(supplier=obj.supplier) &
                models.Q(created__icontains=date)
            )
        else:
            allocations = self.get_queryset().filter(supplier=obj.supplier)
        total = 0
        for item in allocations:
            total += int(item.quantity)
        return total

    def total_cost(self, obj, date=None):
        if date:
            allocations = self.get_queryset().filter(
                models.Q(supplier=obj.supplier) &
                models.Q(created__icontains=date)
            )
        else:
            allocations = self.get_queryset().filter(supplier=obj.supplier)
        total = 0
        for item in allocations:
            try:
                total += item.total_cost.gross
            except Exception as e:
                print(e)
        return total



@python_2_unicode_compatible
class PurchaseProduct(models.Model):
    variant = models.ForeignKey(
        ProductVariant, related_name='purchase_variant',
        verbose_name=pgettext_lazy('PurchaseProduct item field', 'variant'))
    stock = models.ForeignKey(
        Stock, related_name='purchase_stock',
        verbose_name=pgettext_lazy('PurchaseProduct item field', 'stock'))
    quantity = models.IntegerField(
        pgettext_lazy('PurchaseProduct item field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    cost_price = PriceField(
        pgettext_lazy('PurchaseProduct item field', 'cost price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)
    amount_paid = PriceField(
        pgettext_lazy('PurchaseProduct item field', 'amount paid'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)
    balance = PriceField(
        pgettext_lazy('PurchaseProduct item field', 'balance price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)
    total_cost = PriceField(
        pgettext_lazy('PurchaseProduct item field', 'cost price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)
    supplier = models.ForeignKey(
        Supplier, related_name='purchase_supplier',
        verbose_name=pgettext_lazy('PurchaseProduct item field', 'supplier'), null=True, blank=True)
    invoice_number = models.CharField(
        pgettext_lazy('PurchaseProduct', 'invoice_number'), null=True, max_length=36,)
    payment_number = models.CharField(
        pgettext_lazy('PurchaseProduct field', 'payment_number'), null=True, max_length=36, )
    payment_options = models.ManyToManyField(
        PaymentOption, related_name='purchase_payment_option', blank=True,
        verbose_name=pgettext_lazy('PurchaseProduct item field',
                                   'payment options'))
    created = models.DateTimeField(
        pgettext_lazy('PurchaseProduct field', 'created'),
        default=now, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        verbose_name=pgettext_lazy('PurchaseProduct history entry field', 'user'))
    comment = models.CharField(
        pgettext_lazy('PurchaseProduct field', 'comment'),
        max_length=100, default='', blank=True)

    objects = PurchaseProductManager()

    class Meta:
        verbose_name = pgettext_lazy('PurchaseProduct model', 'PurchaseProduct')
        verbose_name_plural = pgettext_lazy('PurchaseProduct model', 'PurchaseProducts')

    def __str__(self):
        return str(self.variant)+' '+str(self.stock)

    def get_balance(self):
        try:
            return self.total_cost.gross - self.amount_paid.gross
        except:
            return 0

    def get_total_cost(self):
        if not self.cost_price:
            # return self.cost_price.gross * self.quantity
            # return self.stock.variant.get_price_per_item().gross * self.quantity
            return 0
        return self.cost_price.gross * self.quantity

    def get_cost_price(self):
        if not self.cost_price:
            # return self.stock.cost_price
            return self.stock.variant.get_price_per_item().gross
        return self.cost_price

    def get_supplier_credit_balance(self):
        return get_supplier_credit_balance(self.supplier)

    def get_supplier_credit_total(self):
        return get_supplier_credit_total(self.supplier)


class PurchasedItem(models.Model):
    purchase = models.ForeignKey(PurchaseVariant, related_name='purchased_item', on_delete=models.CASCADE)
    order = models.IntegerField(default=Decimal(1))
    sku = models.CharField(
        pgettext_lazy('PurchasedItem field', 'SKU'), max_length=32)
    quantity = models.IntegerField(
        pgettext_lazy('PurchasedItem field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    product_name = models.CharField(
        pgettext_lazy('PurchasedItem field', 'product name'), max_length=128)
    total_cost = models.DecimalField(
        pgettext_lazy('PurchasedItem field', 'total cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    unit_cost = models.DecimalField(
        pgettext_lazy('PurchasedItem field', 'unit cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    total_cost = models.DecimalField(
        pgettext_lazy('PurchasedItem field', 'total cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    unit_purchase = models.DecimalField(
        pgettext_lazy('PurchasedItem field', 'unit purchase'), default=Decimal(0), max_digits=100, decimal_places=2)
    total_purchase = models.DecimalField(
        pgettext_lazy('PurchasedItem field', 'total purchase'), default=Decimal(0), max_digits=100, decimal_places=2)

    created = models.DateTimeField(
        pgettext_lazy('PurchasedItem field', 'created'),
        default=now, editable=False)

    class Meta:
        # unique_together = ('sales')
        ordering = ['order']

    def __unicode__(self):
        return '%d: %s' % (self.order, self.product_name)

    def __str__(self):
        return self.product_name


@python_2_unicode_compatible
class PurchaseOrder(models.Model):
    product = models.ForeignKey(
        Product,blank=True,null=True,related_name='products',
        verbose_name=pgettext_lazy('PurchaseOrder field', 'product'))
    status = models.CharField(
        pgettext_lazy('PurchaseOrder field', 'purchase order status'),
        max_length=32, choices=OrderStatus.CHOICES, default=OrderStatus.PENDING)
    created = models.DateTimeField(
        pgettext_lazy('PurchaseOrder field', 'created'),
        default=now, editable=False)
    last_status_change = models.DateTimeField(
        pgettext_lazy('PurchaseOrder field', 'last status change'),
        default=now, editable=False)
    customer = models.ForeignKey(
        Customer, blank=True, null=True, related_name='ordercustomers',
        verbose_name=pgettext_lazy('PurchaseOrder field', 'customer'))
    supplier = models.ForeignKey(
        Supplier, blank=True, null=True, related_name='ordersuppliers',
        verbose_name=pgettext_lazy('PurchaseOrder field', 'supplier'))

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='orderusers',
        verbose_name=pgettext_lazy('PurchaseOrder field', 'user'))
    language_code = models.CharField(max_length=35, default=settings.LANGUAGE_CODE)
    billing_address = models.ForeignKey(
        Address, related_name='+', editable=False,blank=True, null=True,
        verbose_name=pgettext_lazy('PurchaseOrder field', 'billing address'))
    user_email = models.EmailField(
        pgettext_lazy('PurchaseOrder field', 'user email'),
        blank=True, default='', editable=False)
    lfo_number = models.CharField(
        pgettext_lazy('PurchaseOrder field', 'local purchase order number'), null=True, max_length=36,)


    class Meta:
        ordering = ('-last_status_change',)
        verbose_name = pgettext_lazy('PurchaseOrder model', 'PurchaseOrder')
        verbose_name_plural = pgettext_lazy('PurchaseOrder model', 'PurchaseOrder')

    def __str__(self):
        return str(self.lfo_number)+' '+str(self.product)

class PurchaseItems(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder,related_name='purchaseitems',on_delete=models.CASCADE)
    order = models.IntegerField(default=Decimal(1))
    sku = models.CharField(
        pgettext_lazy('PurchaseItems field', 'SKU'), max_length=32)
    quantity = models.IntegerField(
        pgettext_lazy('PurchaseItems field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    product_name = models.CharField(
        pgettext_lazy('PurchaseItems field', 'product name'), max_length=128)


    class Meta:
        #unique_together = ('sales')
        ordering = ['order']
    def __str__(self):
        return self.purchase_order

    def __unicode__(self):
        return '%s: %s' % (self.sku,self.product_name)



