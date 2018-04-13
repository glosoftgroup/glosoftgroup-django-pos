from __future__ import unicode_literals

from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy
from django_prices.models import PriceField
from jsonfield import JSONField
from django.contrib.postgres.fields import HStoreField

from django.utils import timezone
from datetime import datetime, timedelta
from ..userprofile.models import Address
from ..customer.models import Customer
from ..site.models import SiteSettings
from ..sale.models import Terminal, PaymentOption
from . import OrderStatus


class CreditManager(models.Manager):
    def due_credits(self):        
        return self.get_queryset().filter(due_date__lte=timezone.now())

    def customer_credits(self, customer):
        return self.get_queryset().filter(customer=customer).aggregate(Sum('debt'))['debt__sum']

    def expired_credit(self):        
        max_credit_date = SiteSettings.objects.get(pk=1).max_credit_date 
        days = timezone.now()-timedelta(days=max_credit_date)
        return self.get_queryset().filter(created__lte=timezone.now()-timedelta(days=max_credit_date))


class Credit(models.Model):
    status = models.CharField(
        pgettext_lazy('Credit field', 'Credit status'),
        max_length=32, choices=OrderStatus.CHOICES, default=OrderStatus.NEW)
    created = models.DateTimeField(
        pgettext_lazy('Credit field', 'created'),
        default=now, editable=False)    
    last_status_change = models.DateTimeField(
        pgettext_lazy('Credit field', 'last status change'),
        default=now, editable=False)
    customer = models.ForeignKey(
        Customer, blank=True, null=True, related_name='credit_customers',
        verbose_name=pgettext_lazy('Credit field', 'customer'))

    mobile = models.CharField(max_length=20, blank=True, null=True)
    customer_name = models.CharField(max_length=100, null=True, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='creditor',
        verbose_name=pgettext_lazy('Credit field', 'user'))
    language_code = models.CharField(max_length=35, default=settings.LANGUAGE_CODE)
    billing_address = models.ForeignKey(
        Address, related_name='+', editable=False,blank=True, null=True,
        verbose_name=pgettext_lazy('Credit field', 'billing address'))
    user_email = models.EmailField(
        pgettext_lazy('Credit field', 'user email'),
        blank=True, default='', editable=False)
    terminal = models.ForeignKey(
        Terminal, related_name='terminal_credit',blank=True, default='',
        verbose_name=pgettext_lazy('Credit field', 'order'))
    invoice_number = models.CharField(
        pgettext_lazy('Credit field', 'invoice_number'), unique=True, null=True, max_length=36,)
    
    total_net = models.DecimalField(
        pgettext_lazy('Credit field', 'total net'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    sub_total = models.DecimalField(
        pgettext_lazy('Credit field', 'sub total'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    total_tax = models.DecimalField(
        pgettext_lazy('Credit field', 'total tax'), default=Decimal(0), max_digits=100, decimal_places=2)
    amount_paid = models.DecimalField(
        pgettext_lazy('Credit field', 'amount paid'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    balance = models.DecimalField(
        pgettext_lazy('Credit field', 'balance'), default=Decimal(0), max_digits=100, decimal_places=2)
    debt = models.DecimalField(
        pgettext_lazy('Credit field', 'debt'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    discount_amount = PriceField(
        verbose_name=pgettext_lazy('Credit field', 'discount amount'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)
    discount_name = models.CharField(
        verbose_name=pgettext_lazy('Credit field', 'discount name'),
        max_length=255, default='', blank=True)
    payment_options = models.ManyToManyField(
        PaymentOption, related_name='credit_payment_option', blank=True,
        verbose_name=pgettext_lazy('Credit field',
                                   'credit options'))
    notified = models.BooleanField(default=False, blank=False)

    due_date = models.DateTimeField(
        pgettext_lazy('Credit field', 'due date'),
        null=False, default=now)
    payment_data = JSONField(null=True, blank=True)
    
    objects = CreditManager()

    class Meta:
        ordering = ('-last_status_change',)
        verbose_name = pgettext_lazy('Credit model', 'Credit')
        verbose_name_plural = pgettext_lazy('Credit model', 'Credits')
        
    def __str__(self):
        return self.invoice_number

    def __unicode__(self):
        return unicode(self.invoice_number)

    def total_items(self):
        return len(self.credititems.all())

    def items(self):
        return self.credititems.all()

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

    def total_amount(self):
        return len(self.credit_history.all())

    def total_balance(self):
        return self.credit_history.aggregate(Sum('balance'))['balance__sum']

                                
class CreditedItem(models.Model):
    credit = models.ForeignKey(Credit,related_name='credititems',on_delete=models.CASCADE)
    order = models.IntegerField(default=Decimal(1))
    sku = models.CharField(
        pgettext_lazy('CreditedItem field', 'SKU'), max_length=32)    
    quantity = models.IntegerField(
        pgettext_lazy('CreditedItem field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    product_name = models.CharField(
        pgettext_lazy('CreditedItem field', 'product name'), max_length=128)
    total_cost = models.DecimalField(
        pgettext_lazy('CreditedItem field', 'total cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    unit_cost = models.DecimalField(
        pgettext_lazy('CreditedItem field', 'unit cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    product_category = models.CharField(
        pgettext_lazy('CreditedItem field', 'product_category'), max_length=128, null=True)
    discount = models.DecimalField(
        pgettext_lazy('CreditedItem field', 'discount'), default=Decimal(0), max_digits=100, decimal_places=2)
    tax = models.DecimalField(
        pgettext_lazy('CreditedItem field', 'tax'), default=Decimal(0), max_digits=100, decimal_places=2)
    attributes = HStoreField(
        pgettext_lazy('CreditedItem field', 'attributes'), default={})

    unit_purchase = models.DecimalField(
        pgettext_lazy('SoldItem field', 'unit purchase'), default=Decimal(0), max_digits=100, decimal_places=2)
    total_purchase = models.DecimalField(
        pgettext_lazy('SoldItem field', 'total purchase'), default=Decimal(0), max_digits=100, decimal_places=2)

    class Meta:
        #unique_together = ('sales')
        ordering = ['order']
    def __unicode__(self):
        return '%d: %s' % (self.order,self.product_name)

    def __str__(self):
        return self.product_name


@python_2_unicode_compatible
class CreditHistoryEntry(models.Model):
    date = models.DateTimeField(
        pgettext_lazy('Credit history entry field', 'last history change'),
        default=now, editable=False)
    created = models.DateTimeField(
        pgettext_lazy('Credit history entry field', 'created'),
        default=now, editable=False)
    credit = models.ForeignKey(
        Credit, related_name='credit_history',
        verbose_name=pgettext_lazy('Credit history entry field', 'order'))
    amount = models.DecimalField(
        pgettext_lazy('Credit history entry field', 'amount cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    balance = models.DecimalField(
        pgettext_lazy('Credit history entry field', 'balance'), default=Decimal(0), max_digits=100,
        decimal_places=2)

    comment = models.CharField(
        pgettext_lazy('Credit history entry field', 'comment'),
        max_length=100, default='', blank=True)
    crud = models.CharField(
        pgettext_lazy('Credit history entry field', 'crud'),
        max_length=30, default='', blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        verbose_name=pgettext_lazy('Credit history entry field', 'user'))

    class Meta:
        ordering = ('date',)
        verbose_name = pgettext_lazy(
            'Credit history entry model', 'Credit history entry')
        verbose_name_plural = pgettext_lazy(
            'Credit history entry model', 'Credit history entries')

    def __str__(self):
        return pgettext_lazy(
            'Credit history entry str',
            'CreditHistoryEntry for terminal #%s') % self.credit.invoice_number





