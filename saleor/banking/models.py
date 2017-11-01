from __future__ import unicode_literals
from django.db import models
from django.utils.translation import pgettext_lazy
from decimal import Decimal


class Bank(models.Model):
    name = models.CharField(
        pgettext_lazy('Bank field', 'Bank name'),
        max_length=52, )

    class Meta:
        verbose_name = pgettext_lazy('Bank model', 'Bank')
        verbose_name_plural = pgettext_lazy('Banks model', 'Banks')

    def __str__(self):
        return str(self.name)

class Account(models.Model):
    name = models.CharField(
        pgettext_lazy('Account field', 'Account name'),
        max_length=52, )
    number = models.IntegerField(default=Decimal(1))
    bank = models.ForeignKey(Bank, related_name='bank', on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = pgettext_lazy('Account model', 'Account')
        verbose_name_plural = pgettext_lazy('Accounts model', 'Accounts')

    def __str__(self):
        return str(self.name)

