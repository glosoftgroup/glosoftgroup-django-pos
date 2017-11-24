from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from django.db.models import F
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import pgettext_lazy
from django_countries.fields import Country, CountryField


class AddressBookManager(models.Manager):

    def as_data(self, address):
        data = model_to_dict(addressbook, exclude=['id', 'user'])
        if isinstance(data['country'], Country):
            data['country'] = data['country'].code
        return data

    def are_identical(self, addr1, addr2):
        data1 = self.as_data(addr1)
        data2 = self.as_data(addr2)
        return data1 == data2

    def store_address(self, user, address):
        data = self.as_data(address)
        address, dummy_created = user.addresses.get_or_create(**data)
        return address


@python_2_unicode_compatible
class AddressBook(models.Model):
    first_name = models.CharField(
        pgettext_lazy('AddressBook field', 'given name'),
        max_length=256, blank=True)
    last_name = models.CharField(
        pgettext_lazy('AddressBook field', 'family name'),
        max_length=256, blank=True)
    company_name = models.CharField(
        pgettext_lazy('AddressBook field', 'company or organization'),
        max_length=256, blank=True)
    street_address_1 = models.CharField(
        pgettext_lazy('AddressBook field', 'address'),
        max_length=256, blank=True)
    street_address_2 = models.CharField(
        pgettext_lazy('AddressBook field', 'address'),
        max_length=256, blank=True)
    city = models.CharField(
        pgettext_lazy('AddressBook field', 'city'),
        max_length=256, blank=True)
    city_area = models.CharField(
        pgettext_lazy('AddressBook field', 'district'),
        max_length=128, blank=True)
    postal_code = models.CharField(
        pgettext_lazy('AddressBook field', 'postal code'),
        max_length=20, blank=True)
    country = CountryField(
        pgettext_lazy('AddressBook field', 'country'))
    country_area = models.CharField(
        pgettext_lazy('AddressBook field', 'state or province'),
        max_length=128, blank=True)
    phone = models.CharField(
        pgettext_lazy('AddressBook field', 'phone number'),
        max_length=30, blank=True)    
    objects = AddressBookManager()

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)
    

    class Meta:
        verbose_name = pgettext_lazy('AddressBook model', 'address book')
        verbose_name_plural = pgettext_lazy('AddressBook model', 'address books')

    def __str__(self):
        if self.company_name:
            return '%s - %s' % (self.company_name, self.full_name)
        return self.full_name

    def __repr__(self):
        return (
            'AddressBook(first_name=%r, last_name=%r, company_name=%r, '
            'street_address_1=%r, street_address_2=%r, city=%r, '
            'postal_code=%r, country=%r, country_area=%r, phone=%r)' % (
                self.first_name, self.last_name, self.company_name,
                self.street_address_1, self.street_address_2, self.city,
                self.postal_code, self.country, self.country_area,
                self.phone))


class CustomerManager(BaseUserManager):

    def create_customer(self, email, password=None,
                    is_active=True, username='', **extra_fields):
        'Creates a User with the given username, email and password'
        email = CustomerManager.normalize_email(email)
        customer = self.model(email=email, is_active=is_active,
                           **extra_fields)
        if password:
            customer.set_password(password)
        customer.save()
        return customer

    def redeem_points(self, customer, points):
        customer.loyalty_points = F('loyalty_points') - points        
        customer.redeemed_loyalty_points = F('redeemed_loyalty_points') + points
        customer.save(update_fields=['loyalty_points', 'redeemed_loyalty_points'])
    
    def gain_points(self, customer, points):
        customer.loyalty_points = F('loyalty_points') + points        
        customer.save(update_fields=['loyalty_points'])

    

class Customer(models.Model):
    email = models.EmailField(pgettext_lazy('Customer field', 'email'), null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    addresses = models.ManyToManyField(
        AddressBook, blank=True,
        verbose_name=pgettext_lazy('Customer field', 'addresses'))   
    is_active = models.BooleanField(
        pgettext_lazy('Customer field', 'active'),
        default=True)
    creditable = models.BooleanField(default=False)
    loyalty_points = models.IntegerField(
        pgettext_lazy('Customer field', 'loyalty points'), default=0)    
    redeemed_loyalty_points = models.IntegerField(
        pgettext_lazy('Customer field', 'Redeemed loyalty points'), default=0)    
    
    nid = models.CharField(max_length=100, null=True,blank=True)
    mobile = models.CharField(max_length=100, null=True, blank=True)
    image = models.FileField(upload_to='employee', blank=True, null=True)
    date_joined = models.DateTimeField(
        pgettext_lazy('Customer field', 'date joined'),
        default=timezone.now, editable=False)
    default_shipping_address = models.ForeignKey(
        AddressBook, related_name='+', null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=pgettext_lazy('Customer field', 'default shipping address'))
    default_billing_address = models.ForeignKey(
        AddressBook, related_name='+', null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=pgettext_lazy('Customer field', 'default billing address'))    

    objects = CustomerManager()

    class Meta:
        verbose_name = pgettext_lazy('Customer model', 'customer')
        verbose_name_plural = pgettext_lazy('Customer model', 'customers')

    def __str__(self):
        return self.name

    def get_full_name(self):
        return self.email
        
    def is_creditable_check_box(self):
        if self.creditable:
            return "checked='checked'"
        return ''

    def get_short_name(self):
        return self.email

    def get_sales(self):
        return len(self.customers.all())

    def get_total_discount(self):
        total = self.customers.aggregate(models.Sum('discount_amount'))['discount_amount__sum']
        if total:
            return cool_format(total)
        return '--'

    def get_total_sales_amount(self):
        total = self.customers.aggregate(models.Sum('total_net'))['total_net__sum']
        if total:
            return cool_format(total)+' '+settings.DEFAULT_CURRENCY
        return '--'

    def get_total_credit_amount(self):
        total = self.credit_customers.aggregate(models.Sum('debt'))['debt__sum']
        if total:
            return cool_format(total)+' '+settings.DEFAULT_CURRENCY
        return '--'

    def get_credits(self):
        return len(self.credit_customers.all())    

    def get_loyalty_points(self):
        if self.loyalty_points != 0.00:
            return cool_int_format(self.loyalty_points)
        return 0

    def get_redeemed_loyalty_points(self):
        if self.redeemed_loyalty_points != 0:
            return cool_int_format(self.redeemed_loyalty_points)
        return 0

    def get_loy_perc(self):        
        redeemed = self.redeemed_loyalty_points
        loyalty  = self.loyalty_points
        total = redeemed + loyalty       
        if not total:
            return 0
        return (100*loyalty)/total

    def get_rem_perc(self):        
        redeemed = self.redeemed_loyalty_points
        loyalty  = self.loyalty_points
        total = redeemed + loyalty        
        if not total:
            return 0.00
        return (100*redeemed)/total


def cool_int_format(value):
     value = int(value)
     if value >= 1000:
         return str('{0:,}'.format(value))
     return str(value)


def cool_format(value):
    value = Decimal(value)
    if value >= 1000.00:
        return str('{0:,}'.format(value))
    return str(value)
