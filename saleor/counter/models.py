from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.utils.translation import pgettext_lazy
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.utils.timezone import now
import datetime


class CounterManager(BaseUserManager):
    def available_counter(self):
        today = datetime.date.today()
        return self.item_counter.filter(
            Q(transfer__date__lt=today),
            Q(closed=True))


class Counter(models.Model):
    name = models.CharField(
        pgettext_lazy('Counter field', 'name'), unique=True, max_length=128)
    description = models.TextField(
        verbose_name=pgettext_lazy('Counter field', 'description'), blank=True, null=True)
    updated_at = models.DateTimeField(
        pgettext_lazy('Counter field', 'updated at'), auto_now=True, null=True)
    created = models.DateTimeField(pgettext_lazy('Counter field', 'created'),
                                   default=now, editable=False)
    objects = CounterManager()

    class Meta:
        app_label = 'counter'
        verbose_name = pgettext_lazy('Counter model', 'Counters')
        verbose_name_plural = pgettext_lazy('Counters model', 'Counters')

    def __str__(self):
        return self.name

    def is_closed(self):
        today = datetime.date.today()
        try:
            transfers = self.item_counter.filter(transfer__date__lt=today, closed=False)
            if not transfers.exists():
                return True
            return False
        except:
            return True

    def last_open(self):
        try:
            transfers = self.item_counter.filter(closed=False).first()
            return transfers.transfer.date
        except:
            return ''
