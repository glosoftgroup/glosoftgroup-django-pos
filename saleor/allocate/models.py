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

from django.utils import timezone
from payments import PaymentStatus, PurchasedItem
from payments.models import BasePayment
from prices import Price, FixedDiscount
from django.db.models import F
from satchless.item import ItemLine, ItemSet
from datetime import date, datetime, timedelta

from ..discount.models import Voucher
from ..product.models import Product
from ..userprofile.models import Address
from ..customer.models import Customer
from ..site.models import SiteSettings
from ..sale.models import Terminal, PaymentOption
from ..car.models import Car

from . import OrderStatus
from . import TransactionStatus

class AllocateManager(models.Manager):
    def due_credits(self):        
        return self.get_queryset().filter(due_date__lte=timezone.now())

    def expired_credit(self):        
        max_credit_date = SiteSettings.objects.get(pk=1).max_credit_date 
        days = timezone.now()-timedelta(days=max_credit_date)
        return self.get_queryset().filter(created__lte=timezone.now()-timedelta(days=max_credit_date))


class Allocate(models.Model):
    status = models.CharField(
        pgettext_lazy('Allocate field', 'Allocate status'),
        max_length=32, choices=OrderStatus.CHOICES, default=OrderStatus.NEW)
    created = models.DateTimeField(
        pgettext_lazy('Allocate field', 'created'),
        default=now, editable=False)    
    last_status_change = models.DateTimeField(
        pgettext_lazy('Allocate field', 'last status change'),
        default=now, editable=False)
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='shop_agent',
        verbose_name=pgettext_lazy('Allocate field', 'agent'))

    mobile = models.CharField(max_length=20, blank=True, null=True)
    customer_name = models.CharField(max_length=100, null=True, blank=True)
    car = models.ForeignKey(Car, blank=True, null=True, related_name='transfer_car',
        verbose_name=pgettext_lazy('Allocate field', 'Transfer Car'))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='allocator',
        verbose_name=pgettext_lazy('Allocate field', 'user'))
    language_code = models.CharField(max_length=35, default=settings.LANGUAGE_CODE)
    billing_address = models.ForeignKey(
        Address, related_name='allocate_bill', editable=False,blank=True, null=True,
        verbose_name=pgettext_lazy('Allocate field', 'billing address'))
    user_email = models.EmailField(
        pgettext_lazy('Allocate field', 'user email'),
        blank=True, default='', editable=False)
    terminal = models.ForeignKey(
        Terminal, related_name='terminal_allocate',blank=True, default='',
        verbose_name=pgettext_lazy('Allocate field', 'order'))
    invoice_number = models.CharField(
        pgettext_lazy('Allocate field', 'invoice_number'), unique=True, null=True, max_length=36,)
    
    total_net = models.DecimalField(
        pgettext_lazy('Allocate field', 'total net'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    sub_total = models.DecimalField(
        pgettext_lazy('Allocate field', 'sub total'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    total_tax = models.DecimalField(
        pgettext_lazy('Allocate field', 'total tax'), default=Decimal(0), max_digits=100, decimal_places=2)
    amount_paid = models.DecimalField(
        pgettext_lazy('Allocate field', 'amount paid'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    balance = models.DecimalField(
        pgettext_lazy('Allocate field', 'balance'), default=Decimal(0), max_digits=100, decimal_places=2)
    debt = models.DecimalField(
        pgettext_lazy('Allocate field', 'debt'), default=Decimal(0), max_digits=100, decimal_places=2)

    discount_amount = PriceField(
        verbose_name=pgettext_lazy('Allocate field', 'discount amount'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)
    discount_name = models.CharField(
        verbose_name=pgettext_lazy('Allocate field', 'discount name'),
        max_length=255, default='', blank=True)
    payment_options = models.ManyToManyField(
        PaymentOption, related_name='agent_payment_option', blank=True,
        verbose_name=pgettext_lazy('Sales field',
                                   'sales options'))
    notified = models.BooleanField(default=False, blank=False)

    due_date = models.DateTimeField(
        pgettext_lazy('Allocate field', 'due date'),
        null=False,default=now)
    
    objects = AllocateManager()
    class Meta:
        ordering = ('-last_status_change',)
        verbose_name = pgettext_lazy('Allocate model', 'Allocate')
        verbose_name_plural = pgettext_lazy('Allocate model', 'Allocations')
        
    def __str__(self):
        return self.invoice_number

    def __unicode__(self):
        return unicode(self.invoice_number)

    def total_items(self):
        return len(self.allocated_items.all())

    def items(self):
        return self.allocated_items.all()

    def item_detail(self,sku):
        return self.allocated_items.get(sku=sku)

    def is_fully_paid(self):
        if self.status == 'fully-paid':
            return True
        else:
            return False

    def is_due(self):        
        if self.due_date <= timezone.now():
            return True
        return False

    def is_expired(self):       
        difference = datetime.now() - self.created.replace(tzinfo=None)        
        max_credit_date = SiteSettings.objects.get(pk=1).max_credit_date        
        if difference.days > max_credit_date:
            return True
        return False


class AllocatedItem(models.Model):
    allocate = models.ForeignKey(Allocate,related_name='allocated_items',on_delete=models.CASCADE)
    order = models.IntegerField(default=Decimal(1))
    sku = models.CharField(
        pgettext_lazy('AllocatedItem field', 'SKU'), max_length=32)    
    quantity = models.IntegerField(
        pgettext_lazy('AllocatedItem field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(0))
    allocated_quantity = models.DecimalField(
        pgettext_lazy('AllocatedItem field', 'debt'), default=Decimal(0), max_digits=100, decimal_places=2)

    product_name = models.CharField(
        pgettext_lazy('AllocatedItem field', 'product name'), max_length=128)
    total_cost = models.DecimalField(
        pgettext_lazy('AllocatedItem field', 'total cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    unit_cost = models.DecimalField(
        pgettext_lazy('AllocatedItem field', 'unit cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    product_category = models.CharField(
        pgettext_lazy('AllocatedItem field', 'product_category'), max_length=128, null=True)
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

