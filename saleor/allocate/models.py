from __future__ import unicode_literals

from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy
from django_prices.models import PriceField

from django.utils import timezone
from datetime import datetime, timedelta

from ..userprofile.models import Address
from ..site.models import SiteSettings
from ..sale.models import Terminal, PaymentOption
from ..car.models import Car

from . import OrderStatus


class AllocateManager(models.Manager):
    def car_total_net(self, obj):
        return self.get_queryset().filter(car=obj.car)\
                          .aggregate(sum=models.Sum('total_net'))['sum']

    def total_allocated(self, obj, date):
        if date:
            allocations = self.get_queryset().filter(
                          models.Q(car=obj.car) &
                          models.Q(created__icontains=date)
            )
        else:
            allocations = self.get_queryset().filter(car=obj.car)
        total = 0
        for item in allocations:
            total += item.allocated_items.aggregate(sum=models.Sum('allocated_quantity'))['sum']
        return total

    def total_sold(self, obj):
        allocations = self.get_queryset().filter(car=obj.car)
        total = 0
        for item in allocations:
            total += item.allocated_items.aggregate(sum=models.Sum('sold'))['sum']
        return total

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
    total_sale = models.DecimalField(
        pgettext_lazy('Allocate field', 'total paid'), default=Decimal(0), max_digits=100, decimal_places=2)

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
        null=False, default=now)
    
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

    def sold_items(self):
        total = self.allocated_items.aggregate(sum=models.Sum('sold'))
        return total['sum']

    def unsold_items(self):
        total = self.allocated_items.aggregate(sum=models.Sum('unsold'))
        return total['sum']

    def total_allocated(self):
        total = self.allocated_items.aggregate(sum=models.Sum('allocated_quantity'))
        return total['sum']

    def item_detail(self, stock_id):
        return self.allocated_items.get(stock_id=stock_id)

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
    stock_id = models.IntegerField(default=Decimal(0))
    sku = models.CharField(
        pgettext_lazy('AllocatedItem field', 'SKU'), max_length=32)    
    quantity = models.IntegerField(
        pgettext_lazy('AllocatedItem field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(0))
    allocated_quantity = models.IntegerField(
        pgettext_lazy('AllocatedItem field', 'allocated quantity'), validators=[MinValueValidator(0)], default=Decimal(0))
    sold = models.IntegerField(
        pgettext_lazy('AllocatedItem field', 'sold quantity'), validators=[MinValueValidator(0)], default=Decimal(0))
    unsold = models.IntegerField(
        pgettext_lazy('AllocatedItem field', 'unsold quantity'), validators=[MinValueValidator(0)], default=Decimal(0))

    product_name = models.CharField(
        pgettext_lazy('AllocatedItem field', 'product name'), max_length=128)
    total_cost = models.DecimalField(
        pgettext_lazy('AllocatedItem field', 'total cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    unit_cost = models.DecimalField(
        pgettext_lazy('AllocatedItem field', 'unit cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    minimum_price = models.DecimalField(
        pgettext_lazy('AllocatedItem field', 'minimum price'), default=Decimal(0), max_digits=100, decimal_places=2)
    wholesale_override = models.DecimalField(
        pgettext_lazy('AllocatedItem field', 'wholesale price'), default=Decimal(0), max_digits=100, decimal_places=2)
    low_stock_threshold = models.IntegerField(
        pgettext_lazy('AllocatedItem field', 'low stock threshold'),
        validators=[MinValueValidator(0)], null=True, blank=True, default=Decimal(10))

    unit_purchase = models.DecimalField(
        pgettext_lazy('AllocatedItem field', 'unit purchase'), default=Decimal(0), max_digits=100, decimal_places=2)

    product_category = models.CharField(
        pgettext_lazy('AllocatedItem field', 'product_category'), max_length=128, null=True)
    discount = models.DecimalField(
        pgettext_lazy('SoldItem field', 'discount'), default=Decimal(0), max_digits=100, decimal_places=2)
    tax = models.DecimalField(
        pgettext_lazy('SoldItem field', 'tax'), default=Decimal(0), max_digits=100, decimal_places=2)


    class Meta:
        #unique_together = ('sales')
        ordering = ['order']
    def __unicode__(self):
        return '%d: %s' % (self.order,self.product_name)

    def __str__(self):
        return self.product_name

