from __future__ import unicode_literals

from decimal import Decimal
from uuid import uuid4

import emailit.api
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy
from django_prices.models import PriceField
from payments import PaymentStatus, PurchasedItem
from payments.models import BasePayment
from prices import Price, FixedDiscount
from satchless.item import ItemLine, ItemSet
from datetime import date

from ..discount.models import Voucher
from ..product.models import Product
from ..userprofile.models import Address
from ..customer.models import Customer
from ..site.models import SiteSettings
from ..sale.models import Terminal

from . import OrderStatus
from . import TransactionStatus

class Invoice(models.Model):
    status = models.CharField(
        pgettext_lazy('Invoice field', 'Invoice status'),
        max_length=32, choices=OrderStatus.CHOICES, default=OrderStatus.NEW)
    created = models.DateTimeField(
        pgettext_lazy('Invoice field', 'created'),
        default=now, editable=False)    
    last_status_change = models.DateTimeField(
        pgettext_lazy('Invoice field', 'last status change'),
        default=now, editable=False)
    customer = models.ForeignKey(
        Customer, blank=True, null=True, related_name='invoiced_customers',
        verbose_name=pgettext_lazy('Invoice field', 'customer'))

    mobile = models.CharField(max_length=20, blank=True, null=True)
    customer_name = models.CharField(max_length=100, null=True, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='invoicer',
        verbose_name=pgettext_lazy('Invoice field', 'user'))
    language_code = models.CharField(max_length=35, default=settings.LANGUAGE_CODE)
    billing_address = models.ForeignKey(
        Address, related_name='+', editable=False,blank=True, null=True,
        verbose_name=pgettext_lazy('Invoice field', 'billing address'))
    user_email = models.EmailField(
        pgettext_lazy('Invoice field', 'user email'),
        blank=True, default='', editable=False)
    terminal = models.ForeignKey(
        Terminal, related_name='terminal_invoice',blank=True, default='',
        verbose_name=pgettext_lazy('Invoice field', 'order'))
    invoice_number = models.CharField(
        pgettext_lazy('Invoice field', 'invoice_number'), unique=True, null=True, max_length=36,)
    
    total_net = models.DecimalField(
        pgettext_lazy('Invoice field', 'total net'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    sub_total = models.DecimalField(
        pgettext_lazy('Invoice field', 'sub total'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    total_tax = models.DecimalField(
        pgettext_lazy('Invoice field', 'total tax'), default=Decimal(0), max_digits=100, decimal_places=2)
    amount_paid = models.DecimalField(
        pgettext_lazy('Invoice field', 'amount paid'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    balance = models.DecimalField(
        pgettext_lazy('Invoice field', 'balance'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    discount_amount = PriceField(
        verbose_name=pgettext_lazy('Invoice field', 'discount amount'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)
    discount_name = models.CharField(
        verbose_name=pgettext_lazy('Invoice field', 'discount name'),
        max_length=255, default='', blank=True)
    car_registration = models.CharField(max_length=100, null=True, blank=True)
    class Meta:
        ordering = ('-last_status_change',)
        verbose_name = pgettext_lazy('Invoice model', 'Invoice')
        verbose_name_plural = pgettext_lazy('Invoice model', 'Invoices')
        
    def __str__(self):
        return self.invoice_number
    def __unicode__(self):
        return unicode(self.invoice_number)
                                
class InvoicedItem(models.Model):
    invoice = models.ForeignKey(Invoice,related_name='invoiceitems',on_delete=models.CASCADE)
    order = models.IntegerField(default=Decimal(1))
    sku = models.CharField(
        pgettext_lazy('InvoicedItem field', 'SKU'), max_length=32)    
    quantity = models.IntegerField(
        pgettext_lazy('InvoicedItem field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    product_name = models.CharField(
        pgettext_lazy('InvoicedItem field', 'product name'), max_length=128)
    total_cost = models.DecimalField(
        pgettext_lazy('InvoicedItem field', 'total cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    unit_cost = models.DecimalField(
        pgettext_lazy('InvoicedItem field', 'unit cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    product_category = models.CharField(
        pgettext_lazy('InvoicedItem field', 'product_category'), max_length=128, null=True)
    discount = models.DecimalField(
        pgettext_lazy('SoldItem field', 'discount'), default=Decimal(0), max_digits=100, decimal_places=2)
    tax = models.IntegerField(default=Decimal(0))
    

    class Meta:
        #unique_together = ('sales')
        ordering = ['order']
    def __unicode__(self):
        return '%d: %s' % (self.order,self.product_name)

    def __str__(self):
        return self.product_name

