from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy
from jsonfield import JSONField
from django.contrib.postgres.fields import HStoreField
from ..userprofile.models import Address
from ..customer.models import Customer
from ..site.models import SiteSettings

from . import OrderStatus
from . import TransactionStatus


class PaymentOption(models.Model):
    name = models.CharField(
        pgettext_lazy('Payment option field', 'payment option name'),
        max_length=52, unique=True, )
    description = models.TextField(
        pgettext_lazy('Payment option field', 'description'), blank=True)
    loyalty_point_equiv = models.DecimalField(
        pgettext_lazy('Payment option field', 'loyalty points'), default=Decimal(0), max_digits=100, decimal_places=2)

    class Meta:
        verbose_name = pgettext_lazy('Payment option model', 'Payment')
        verbose_name_plural = pgettext_lazy('Payment options model', 'Payments')

    def __str__(self):
        return str(self.name)


class Terminal(models.Model):
    terminal_name = models.CharField(
        pgettext_lazy('Terminal field', 'terminal name'),
        max_length=52, )
    terminal_number = models.IntegerField(default=Decimal(0))
    created = models.DateTimeField(
        pgettext_lazy('Terminal field', 'created'),
        default=now, editable=False)
    amount = models.IntegerField(default=Decimal(0))

    class Meta:
        verbose_name = pgettext_lazy('Terminal model', 'Terminal')
        verbose_name_plural = pgettext_lazy('Terminals model', 'Terminals')

    def __str__(self):
        return str(self.terminal_name) + ' #' + str(self.terminal_number)

    def get_transations(self):
        return len(self.terminals.all())

    def get_sales(self):
        return len(self.terminal_sales.all())

    def get_todaySales(self):
        return len(self.terminal_sales.filter(created=now()))

    def get_loyalty_points(self):
        points = SiteSettings.objects.get(pk=1)
        return points.loyalty_point_equiv


@python_2_unicode_compatible
class TerminalHistoryEntry(models.Model):
    date = models.DateTimeField(
        pgettext_lazy('Terminal history entry field', 'last history change'),
        default=now, editable=False)
    terminal = models.ForeignKey(
        Terminal, related_name='history',
        verbose_name=pgettext_lazy('Terminal history entry field', 'order'))

    comment = models.CharField(
        pgettext_lazy('Terminal history entry field', 'comment'),
        max_length=100, default='', blank=True)
    crud = models.CharField(
        pgettext_lazy('Terminal history entry field', 'crud'),
        max_length=30, default='', blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        verbose_name=pgettext_lazy('Terminal history entry field', 'user'))

    class Meta:
        ordering = ('date',)
        verbose_name = pgettext_lazy(
            'Terminal history entry model', 'Terminal history entry')
        verbose_name_plural = pgettext_lazy(
            'Terminal history entry model', 'Terminal history entries')

    def __str__(self):
        return pgettext_lazy(
            'Terminal history entry str',
            'TerminalHistoryEntry for terminal #%d') % self.terminal.pk


@python_2_unicode_compatible
class Sales(models.Model):
    status = models.CharField(
        pgettext_lazy('Sales field', 'sales status'),
        max_length=32, choices=OrderStatus.CHOICES, default=OrderStatus.NEW)
    created = models.DateTimeField(
        pgettext_lazy('Sales field', 'created'),
        default=now, editable=False)
    transfer = models.BooleanField(default=False, blank=False)
    last_status_change = models.DateTimeField(
        pgettext_lazy('Sales field', 'last status change'),
        default=now, editable=False)
    customer = models.ForeignKey(
        Customer, blank=True, null=True, related_name='customers',
        verbose_name=pgettext_lazy('Sales field', 'customer'))

    mobile = models.CharField(max_length=20, blank=True, null=True)
    customer_name = models.CharField(max_length=100, null=True, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='users',
        verbose_name=pgettext_lazy('Sales field', 'user'))
    language_code = models.CharField(max_length=35, default=settings.LANGUAGE_CODE)
    billing_address = models.ForeignKey(
        Address, related_name='+', editable=False, blank=True, null=True,
        verbose_name=pgettext_lazy('Sales field', 'billing address'))
    user_email = models.EmailField(
        pgettext_lazy('Sales field', 'user email'),
        blank=True, default='', editable=False)
    terminal = models.ForeignKey(
        Terminal, related_name='terminal_sales', blank=True, default='',
        verbose_name=pgettext_lazy('Sales field', 'order'))
    invoice_number = models.CharField(
        pgettext_lazy('Sales field', 'invoice_number'), unique=True, null=True, max_length=36, )

    total_net = models.DecimalField(
        pgettext_lazy('Sales field', 'total net'), default=Decimal(0), max_digits=100, decimal_places=2)
    total_tax = models.DecimalField(
        pgettext_lazy('Sales field', 'total tax'), default=Decimal(0), max_digits=100, decimal_places=2)
    sub_total = models.DecimalField(
        pgettext_lazy('Sales field', 'sub total'), default=Decimal(0), max_digits=100, decimal_places=2)

    total_tax = models.DecimalField(
        pgettext_lazy('Sales field', 'total tax'), default=Decimal(0), max_digits=100, decimal_places=2)
    amount_paid = models.DecimalField(
        pgettext_lazy('Sales field', 'amount paid'), default=Decimal(0), max_digits=100, decimal_places=2)

    balance = models.DecimalField(
        pgettext_lazy('Sales field', 'balance'), default=Decimal(0), max_digits=100, decimal_places=2)

    discount_amount = models.DecimalField(
        pgettext_lazy('Sales field', 'total discount'), default=Decimal(0), max_digits=100, decimal_places=2)

    discount_name = models.CharField(
        verbose_name=pgettext_lazy('Sales field', 'discount name'),
        max_length=255, default='', blank=True)
    payment_options = models.ManyToManyField(
        'PaymentOption', related_name='payment_option', blank=True,
        verbose_name=pgettext_lazy('Sales field',
                                   'sales options'))
    payment_data = JSONField(null=True, blank=True)

    class Meta:
        ordering = ('-last_status_change',)
        verbose_name = pgettext_lazy('Sales model', 'Sales')
        verbose_name_plural = pgettext_lazy('Sales model', 'Sales')

    def __str__(self):
        return self.invoice_number

    def __unicode__(self):
        return unicode(self.invoice_number) 


class SoldItem(models.Model):
    sales = models.ForeignKey(Sales, related_name='solditems', on_delete=models.CASCADE)
    stock_id = models.IntegerField(default=Decimal(0))
    order = models.IntegerField(default=Decimal(1))
    sku = models.CharField(
        pgettext_lazy('SoldItem field', 'SKU'), max_length=32)
    quantity = models.IntegerField(
        pgettext_lazy('SoldItem field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    product_name = models.CharField(
        pgettext_lazy('SoldItem field', 'product name'), max_length=128)
    total_cost = models.DecimalField(
        pgettext_lazy('SoldItem field', 'total cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    unit_cost = models.DecimalField(
        pgettext_lazy('SoldItem field', 'unit cost'), default=Decimal(0), max_digits=100, decimal_places=2)

    minimum_price = models.DecimalField(
        pgettext_lazy('SoldItem field', 'minimum price'), default=Decimal(0), max_digits=100, decimal_places=2)
    wholesale_override = models.DecimalField(
        pgettext_lazy('SoldItem field', 'wholesale price'), default=Decimal(0), max_digits=100, decimal_places=2)

    unit_purchase = models.DecimalField(
        pgettext_lazy('SoldItem field', 'unit purchase'), default=Decimal(0), max_digits=100, decimal_places=2)
    total_purchase = models.DecimalField(
        pgettext_lazy('SoldItem field', 'total purchase'), default=Decimal(0), max_digits=100, decimal_places=2)

    low_stock_threshold = models.IntegerField(
        pgettext_lazy('SoldItem field', 'low stock threshold'),
        validators=[MinValueValidator(0)], null=True, blank=True, default=Decimal(10))

    product_category = models.CharField(
        pgettext_lazy('SoldItem field', 'product_category'), max_length=128, null=True)
    discount = models.DecimalField(
        pgettext_lazy('SoldItem field', 'discount'), default=Decimal(0), max_digits=100, decimal_places=2)

    tax = models.DecimalField(default=Decimal(0), max_digits=100, decimal_places=2)
    attributes = HStoreField(
        pgettext_lazy('SoldItem field', 'attributes'), default={})
    created = models.DateTimeField(
        pgettext_lazy('SoldItem field', 'created'),
        default=now, editable=False)

    class Meta:
        # unique_together = ('sales')
        ordering = ['order']

    def __unicode__(self):
        return '%d: %s' % (self.order, self.product_name)

    def __str__(self):
        return self.product_name


class DrawerCash(models.Model):
    trans_type = models.CharField(
        pgettext_lazy('DrawerCash field', 'drawer trans type'),
        max_length=32, choices=TransactionStatus.CHOICES, default=TransactionStatus.DEPOSIT)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='cashier',
        verbose_name=pgettext_lazy('DrawerCash field', 'user'))
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='managers',
        verbose_name=pgettext_lazy('DrawerCash field', 'manager'))
    terminal = models.ForeignKey(Terminal, related_name='terminals',
                                 null=True, blank=True, )
    amount = models.DecimalField(
        pgettext_lazy('DrawerCash field', 'total cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    created = models.DateTimeField(
        pgettext_lazy('DrawerCash field', 'created'),
        default=now, editable=False)
    note = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        verbose_name = pgettext_lazy('DrawerCash model', 'DrawerCash')
        verbose_name_plural = pgettext_lazy('DrawerCash model', 'DrawerCash')

    def __str__(self):
        return str(self.user) + ' ' + str(self.amount)

