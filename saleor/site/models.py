from django.contrib.sites.models import _simple_domain_name_validator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import pgettext_lazy

from . import AuthenticationBackends
from decimal import Decimal
from django.core.validators import MinValueValidator
from datetime import datetime

@python_2_unicode_compatible
class SiteSettings(models.Model):
    domain = models.CharField(
        pgettext_lazy('Site field', 'domain'), max_length=100,
        validators=[_simple_domain_name_validator], unique=True)
    name = models.CharField(pgettext_lazy('Site field', 'name'), max_length=50)
    header_text = models.CharField(
        pgettext_lazy('Site field', 'header text'), max_length=200, blank=True)
    description = models.CharField(
        pgettext_lazy('Site field', 'site description'), max_length=500,
        blank=True)
    loyalty_point_equiv = models.IntegerField( pgettext_lazy('Site field', 'loyalty points equivalency'),
        validators=[MinValueValidator(0)], default=Decimal(0)) 
    opening_time = models.TimeField(pgettext_lazy('Site field', 'opening time'),
        auto_now=False, null=True, blank=True)
    closing_time = models.TimeField(pgettext_lazy('Site field', 'closing time'),
        auto_now=False, null=True, blank=True)
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