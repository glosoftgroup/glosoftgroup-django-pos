from __future__ import unicode_literals
from django.db import models
from django.utils.translation import pgettext_lazy


class Bank(models.Model):
    name = models.CharField(
        pgettext_lazy('Bank field', 'Bank name'),
        max_length=52, )

    class Meta:
        verbose_name = pgettext_lazy('Bank model', 'Bank')
        verbose_name_plural = pgettext_lazy('Banks model', 'Banks')

    def __str__(self):
        return str(self.name)

