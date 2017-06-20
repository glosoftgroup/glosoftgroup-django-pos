from __future__ import unicode_literals

from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import pgettext_lazy
from django_countries.fields import Country, CountryField
from ..search import index
from ..customer.models import AddressBook



class SupplierManager(BaseUserManager):

    def create_supplier(self, email, password=None,
                    is_active=True, username='', **extra_fields):
        'Creates a User with the given username, email and password'
        email = SupplierManager.normalize_email(email)
        supplier = self.model(email=email, is_active=is_active,
                           **extra_fields)        
        supplier.save()
        return supplier
    

class Supplier(models.Model):
    email = models.EmailField(pgettext_lazy('Supplier field', 'email'), unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    addresses = models.ManyToManyField(
        AddressBook, blank=True,
        verbose_name=pgettext_lazy('Supplier field', 'addresses'))   
    is_active = models.BooleanField(
        pgettext_lazy('Supplier field', 'active'),
        default=True)
    nid = models.CharField(max_length=100, null=True,blank=True)
    mobile = models.CharField(max_length=100, null=True, blank=True)
    image = models.FileField(upload_to='staff', blank=True, null=True)
    date_joined = models.DateTimeField(
        pgettext_lazy('Supplier field', 'date joined'),
        default=timezone.now, editable=False)
    default_shipping_address = models.ForeignKey(
        AddressBook, related_name='+', null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=pgettext_lazy('Supplier field', 'default shipping address'))
    default_billing_address = models.ForeignKey(
        AddressBook, related_name='+', null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=pgettext_lazy('Supplier field', 'default billing address'))

    USERNAME_FIELD = 'email'

    objects = SupplierManager()

    search_fields = [
        index.SearchField('email')]

    class Meta:
        verbose_name = pgettext_lazy('Supplier model', 'supplier')
        verbose_name_plural = pgettext_lazy('Supplier model', 'supplier')

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

