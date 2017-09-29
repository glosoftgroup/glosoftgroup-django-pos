from django.contrib.sites.models import _simple_domain_name_validator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import pgettext_lazy

from . import AuthenticationBackends
from decimal import Decimal
from django.core.validators import MinValueValidator
from datetime import datetime
import datetime as t

@python_2_unicode_compatible
class SiteSettings(models.Model):
	domain = models.CharField(
		pgettext_lazy('Site field', 'domain'), max_length=100,
		validators=[_simple_domain_name_validator],blank=True, null=True,default='')
	name = models.CharField(pgettext_lazy('Site field', 'name'),
		max_length=50,blank=True, null=True)
	email = models.EmailField(pgettext_lazy('Site field', 'email'),
		max_length=50,blank=True, null=True)
	header_text = models.CharField(
		pgettext_lazy('Site field', 'header text'), max_length=200, blank=True)
	description = models.CharField(
		pgettext_lazy('Site field', 'site description'), max_length=500,
		blank=True)
	loyalty_point_equiv = models.IntegerField( pgettext_lazy('Site field', 'loyalty points equivalency'),
		validators=[MinValueValidator(0)], default=Decimal(0))
	max_credit_date = models.IntegerField( pgettext_lazy('Site field', 'Maximum credit sale expiration in days'),
        validators=[MinValueValidator(0)], unique=True, default=Decimal(0)) 
    
	opening_time = models.TimeField(pgettext_lazy('Site field', 'opening time'),
		default=t.time(6, 00))
	closing_time = models.TimeField(pgettext_lazy('Site field', 'closing time'),
		default=t.time(21, 00))
	sms_gateway_username = models.CharField(
		pgettext_lazy('Site field', 'sms gateway username'), max_length=500,
		blank=True)
	sms_gateway_apikey = models.CharField(
		pgettext_lazy('Site field', 'sms gateway api key'), max_length=500,
		blank=True)
	image = models.ImageField(upload_to='employee', null=True, blank=True)
	def __str__(self):
		return self.name

	def available_backends(self):
		return self.authorizationkey_set.values_list('name', flat=True)


@python_2_unicode_compatible
class AuthorizationKey(models.Model):
    site_settings = models.ForeignKey(SiteSettings)
    name = models.CharField(
        pgettext_lazy('Authentication field', 'name'), max_length=20,
        choices=AuthenticationBackends.BACKENDS)
    key = models.TextField(pgettext_lazy('Authentication field', 'key'))
    password = models.TextField(
        pgettext_lazy('Authentication field', 'password'))

    class Meta:
        unique_together = (('site_settings', 'name'),)

    def __str__(self):
        return self.name

    def key_and_secret(self):
        return self.key, self.password


class Bank(models.Model):
	name = models.CharField(max_length=100, null=True, blank=True)

	def __str__(self):
		return str(self.name)

class BankBranch(models.Model):
	name = models.CharField(max_length=100, null=True, blank=True)
	bank =  models.ForeignKey(Bank, related_name='branch', max_length=100, null=True, blank=True)

	def __str__(self):
		return str(self.name)

class Department(models.Model):
	name = models.CharField(max_length=100, null=True, blank=True)

	def __str__(self):
		return str(self.name)

class UserRole(models.Model):
	name = models.CharField(max_length=100, null=True, blank=True)

	def __str__(self):
		return str(self.name)

class Files(models.Model):
    file = models.TextField(null=True, blank=True)
    check = models.CharField(max_length=256, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
