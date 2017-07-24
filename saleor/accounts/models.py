from __future__ import unicode_literals

from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy
from payments.models import BasePayment
from prices import Price, FixedDiscount
from satchless.item import ItemLine, ItemSet
from datetime import date

class Expenses(models.Model):
	added_on = models.DateTimeField(default=now, editable=False)
	expense_date = models.CharField(max_length=100, null=True, blank=True)
	voucher = models.CharField(max_length=100, null=True, blank=True)
	expense_type = models.CharField(max_length=100, null=True, blank=True)
	authorized_by = models.CharField(max_length=100, null=True, blank=True)
	received_by = models.CharField(max_length=100, null=True, blank=True)
	paid_to = models.CharField(max_length=100, null=True, blank=True)
	payment_mode = models.CharField(max_length=100, null=True, blank=True)
	account = models.CharField(max_length=100, null=True, blank=True)
	description = models.TextField(max_length=100, null=True, blank=True)
	phone = models.CharField(max_length=100, null=True, blank=True)
	amount = models.CharField(max_length=100, null=True, blank=True)

class ExpenseType(models.Model):
	name = models.CharField(max_length=100, null=True, blank=True)