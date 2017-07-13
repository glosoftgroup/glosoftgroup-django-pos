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
from ..product.models import (
							Product,
							ProductVariant,
							Stock)
from ..userprofile.models import Address
from ..customer.models import Customer
from ..supplier.models import Supplier

from . import OrderStatus

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
	supplier = models.ForeignKey(
		Supplier, related_name='purchase_supplier',
		verbose_name=pgettext_lazy('PurchaseProduct item field', 'supplier')
		,null=True,blank=True)
	invoice_number = models.CharField(
		pgettext_lazy('PurchaseProduct', 'invoice_number'), null=True, max_length=36,)	
	created = models.DateTimeField(
		pgettext_lazy('PurchaseProduct field', 'created'),
		default=now, editable=False)

	class Meta:		
		verbose_name = pgettext_lazy('PurchaseProduct model', 'PurchaseProduct')
		verbose_name_plural = pgettext_lazy('PurchaseProduct model', 'PurchaseProducts')	
	
	def __str__(self):
		return str(self.variant)+' '+str(self.stock)

	def get_total_cost(self):
		if self.cost_price:
			return self.cost_price.gross * self.quantity
		return None

	def get_cost_price(self):
		if not self.cost_price:
			return self.stock.cost_price
		return self.cost_price

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



