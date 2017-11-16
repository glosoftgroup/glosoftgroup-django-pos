from __future__ import unicode_literals

from decimal import Decimal

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy
from django.core.validators import MinValueValidator


class PaymentOption(models.Model):
    name = models.CharField(
        pgettext_lazy('Payment option field', 'payment option name'),
        max_length=52, unique=True, )
    description = models.TextField(
        pgettext_lazy('Payment option field', 'description'), blank=True)
    loyalty_point_equiv = models.IntegerField(pgettext_lazy('Site field', 'loyalty points equivalency'),
                                              validators=[MinValueValidator(0)], default=Decimal(0))

    class Meta:
        verbose_name = pgettext_lazy('Payment option model', 'Payment')
        verbose_name_plural = pgettext_lazy('Payment options model', 'Payments')

    def __str__(self):
        return str(self.name)


@python_2_unicode_compatible
class MpesaPayment(models.Model):
    created = models.DateTimeField(
        pgettext_lazy('MpesaPayment field', 'created'),
        default=now, editable=False)
    # (1. for not used) and (2. for not used)
    status = models.IntegerField( pgettext_lazy('Status', 'status'),
        validators=[MinValueValidator(0)], default=int(1))   
    ref_number = models.CharField(
        pgettext_lazy('MpesaPayment field', 'terminal'),
        null=True, max_length=100,)
    invoice_number = models.CharField(
        pgettext_lazy('MpesaPayment field', 'invoice_number'), null=True, max_length=36,)
    transaction_type = models.CharField(
        pgettext_lazy('MpesaPayment field', 'transation type'), null=True, max_length=36,)
    trans_id = models.CharField(
        pgettext_lazy('MpesaPayment field', 'trans Id'), null=True, max_length=36,)
    trans_time = models.CharField(
        pgettext_lazy('MpesaPayment field', 'trans time'), null=True, max_length=36,)
    business_shortcode = models.CharField(
        pgettext_lazy('MpesaPayment field', 'business shortcode'), null=True, max_length=36,)
    bill_refNumber = models.CharField(
        pgettext_lazy('MpesaPayment field', 'bill reference number'), null=True, max_length=36,)
    phone = models.CharField(
        pgettext_lazy('MpesaPayment field', 'phone'), null=True, max_length=36,)
    first_name = models.CharField(
        pgettext_lazy('MpesaPayment field', 'first name'), null=True, max_length=36,)
    middle_name = models.CharField(
        pgettext_lazy('MpesaPayment field', 'middle name'), null=True, max_length=36,)
    last_name = models.CharField(
        pgettext_lazy('MpesaPayment field', 'last name'), null=True, max_length=36,)

    amount = models.DecimalField(
        pgettext_lazy('MpesaPayment field', 'amount'), default=Decimal(0), max_digits=100, decimal_places=2)

    class Meta:
        verbose_name = pgettext_lazy('MpesaPayment model', 'MpesaPayment')
        verbose_name_plural = pgettext_lazy('MpesaPayments model', 'MpesaPayment')

    # def save(self, *args, **kwargs):
    #     if not self.token:
    #         self.token = str(uuid4())
    #     return super(Order, self).save(*args, **kwargs)

    # def change_status(self, status):
    #     if status != self.status:
    #         self.status = status
    #         self.save()
    def __str__(self):
        return self.phone+' '+self.first_name