from __future__ import unicode_literals
from django.db import models
from django.utils.translation import pgettext_lazy
from decimal import Decimal


class Car(models.Model):
    name = models.CharField(
        pgettext_lazy('Car field', 'Car name'),
        max_length=52, )
    number = models.CharField(
        pgettext_lazy('Car field', 'Car number'),
        max_length=52, )
    car_model = models.CharField(
        pgettext_lazy('Car field', 'Car model'),
        max_length=52, )

    class Meta:
        verbose_name = pgettext_lazy('Car model', 'Car')
        verbose_name_plural = pgettext_lazy('Cars model', 'Cars')

    def __str__(self):
        return str(self.name)


