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

from ..discount.models import Voucher
from ..product.models import Product
from ..userprofile.models import Address

from . import OrderStatus

@python_2_unicode_compatible
class Sales(models.Model):
    status = models.CharField(
        pgettext_lazy('Sales field', 'sales status'),
        max_length=32, choices=OrderStatus.CHOICES, default=OrderStatus.NEW)
    created = models.DateTimeField(
        pgettext_lazy('Sales field', 'created'),
        default=now, editable=False)    
    last_status_change = models.DateTimeField(
        pgettext_lazy('Sales field', 'last status change'),
        default=now, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='users',
        verbose_name=pgettext_lazy('Sales field', 'user'))
    language_code = models.CharField(max_length=35, default=settings.LANGUAGE_CODE)
    billing_address = models.ForeignKey(
        Address, related_name='+', editable=False,blank=True, null=True,
        verbose_name=pgettext_lazy('Sales field', 'billing address'))
    user_email = models.EmailField(
        pgettext_lazy('Sales field', 'user email'),
        blank=True, default='', editable=False)
    terminal = models.CharField(
        pgettext_lazy('Sales field', 'terminal'), null=True, max_length=36,)
    invoice_number = models.CharField(
        pgettext_lazy('Sales field', 'invoice_number'), null=True, max_length=36,)
    
    total_net = models.DecimalField(
        pgettext_lazy('Sales field', 'total net'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    sub_total = models.DecimalField(
        pgettext_lazy('Sales field', 'sub total'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    total_tax = models.DecimalField(
        pgettext_lazy('Sales field', 'total tax'), default=Decimal(0), max_digits=100, decimal_places=2)
    amount_paid = models.DecimalField(
        pgettext_lazy('Sales field', 'amount paid'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    balance = models.DecimalField(
        pgettext_lazy('Sales field', 'balance'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    discount_amount = PriceField(
        verbose_name=pgettext_lazy('Sales field', 'discount amount'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)
    discount_name = models.CharField(
        verbose_name=pgettext_lazy('Sales field', 'discount name'),
        max_length=255, default='', blank=True)
    class Meta:
        ordering = ('-last_status_change',)
        verbose_name = pgettext_lazy('Sales model', 'Sales')
        verbose_name_plural = pgettext_lazy('Sales model', 'Sales')

    # def save(self, *args, **kwargs):
    #     if not self.token:
    #         self.token = str(uuid4())
    #     return super(Order, self).save(*args, **kwargs)

    # def change_status(self, status):
    #     if status != self.status:
    #         self.status = status
    #         self.save()
    def __str__(self):
        return self.invoice_number
class SoldItem(models.Model):
    sales = models.ForeignKey(Sales,related_name='solditems',on_delete=models.CASCADE)
    order = models.IntegerField()
    sku = models.CharField(
        pgettext_lazy('SoldItem field', 'SKU'), max_length=32)    
    quantity = models.IntegerField(
        pgettext_lazy('SoldItem field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    product_name = models.CharField(
        pgettext_lazy('SoldItem field', 'product name'), max_length=128)
    

    class Meta:
        #unique_together = ('sales')
        ordering = ['order']
    def __unicode__(self):
        return '%d: %s' % (self.order,self.product_name)


class Item(models.Model):
    sales = models.ForeignKey(Sales, related_name='items',
     on_delete=models.CASCADE)
    sku = models.CharField(
        pgettext_lazy('Item field', 'SKU'), max_length=32, unique=True)    
    quantity = models.IntegerField(
        pgettext_lazy('item field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    product_name = models.CharField(
        pgettext_lazy('item field', 'product name'), max_length=128)
    
    def __str__(self):
        return self.product_name
    def __unicode__(self):
        return self.sku
    
        