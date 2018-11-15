from __future__ import unicode_literals

from decimal import Decimal
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.conf import settings
from django.utils.translation import pgettext_lazy
from django.utils.timezone import now
from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from saleor.counter.models import Counter
from saleor.product.models import Stock


class TransferManager(BaseUserManager):
    def recharts_items_price(self, start_date=None, end_date=None, *args):
        query = self.all()
        if start_date and end_date is not None:
            query = query.filter(
                models.Q(date__gte=start_date) &
                models.Q(date__lte=end_date)
            )
        else:
            if start_date is not None:
                query = query.filter(date__gte=start_date)
            if end_date is not None:
                query = query.filter(date__lte=end_date)
        query_dates = query.values_list('date').annotate(
            total_item=models.Sum('counter_transfer_items__transferred_qty'))
        items = []
        dates = []
        for d in query_dates:
            dates.append(list(d)[0])
        dates = sorted(dates)
        for date in dates:
            query_date = date
            date_transfers = self.filter(date__icontains=query_date)
            transferred = 0
            sold = 0
            deficit = 0
            for transfer in date_transfers:
                transferred += transfer.counter_transfer_items.all().aggregate(total=models.Sum('total'))['total']
                sold += transfer.counter_transfer_items.all().aggregate(total=models.Sum('total'))['total']
                deficit += transfer.counter_transfer_items.all().aggregate(total=models.Sum('deficit'))['total']
            items.append({
                'name': query_date, 'sold': sold,
                'transferred': transferred, 'deficit': deficit
            })
        return items

    def get_dates(self, date_from, date_to, date, mode, counter=None):
        """
        Return distinct transfer dates between dates
        :param date_from: Date: start date for date range
        :param date_to: Date: end range
        :param date: Date: filter transfer for specific date
        :param mode: string : month, year, range
        :return: a list of dates
        """
        query = self.all()
        if counter:
            query = query.filter(counter__pk=counter)
        if date:
            year = date.split("-")[0]
            if len(date.split('-')) >= 2:
                month = date.split("-")[1]
            else:
                month = "01"
            if mode == "month":
                query = query.filter(date__year=year, date__month=month)
            elif mode == "year":
                query = query.filter(date__year=year)
            else:
                query = query.filter(date__icontains=date)
        elif date_from and date_to:
            if mode:
                year_from = date_from.split("-")[0]
                if len(date_from.split('-')) >= 2:
                    month_from = date_from.split("-")[1]
                else:
                    month_from = "01"

                year_to = date_to.split("-")[0]
                if len(date_to.split('-')) >= 2:
                    month_to = date_to.split("-")[1]
                else:
                    month_to = "01"

                if mode == "month":
                    query = query.filter(date__year__gte=year_from,
                                         date__month__gte=month_from,
                                         date__year__lte=year_to,
                                         date__month__lte=month_to)
                elif mode == "year":
                    query = query.filter(date__year__gte=year_from,
                                         date__year__lte=year_to)
                else:
                    query = query.filter(date__range=[date_from, date_to])
            else:
                query = query.filter(date__range=[date_from, date_to])

        query_dates = query.values_list('date').annotate(
            total_item=models.Sum('counter_transfer_items__transferred_qty'))
        return sorted([list(d)[0] for d in query_dates])

    def recharts_items_filter(self, date_from=None, date_to=None, date=None, mode=None, counter=None):
        dates, items = self.get_dates(date_from, date_to, date, mode, counter), []
        for date in dates:
            query_date = date
            date_transfers = self.filter(date__icontains=query_date)
            transferred, sold, deficit = 0, 0, 0
            for transfer in date_transfers:
                transferred += transfer.counter_transfer_items.all().aggregate(total=models.Sum('transferred_qty'))['total']
                sold += transfer.counter_transfer_items.all().aggregate(total=models.Sum('sold'))['total']
                deficit += transfer.counter_transfer_items.all().aggregate(total=models.Sum('deficit'))['total']
            items.append({
                'name': query_date, 'sold': sold,
                'transferred': transferred, 'deficit': deficit
            })
        return items

    def generate_title(self, title, date_from, date_to, date, mode):
        if date_from and date_to:
            title = title + ' from ' + str(date_from) + ' to ' + str(date_to)
        elif date:
            title = title + str(date)
            del date
        else:
            pass
        return title

    def highcharts_line_filter(self, date_from=None, date_to=None, date=None, mode=None):
        counters, items, series = Counter.objects.all(), [], []
        dates, categories = self.get_dates(date_from, date_to, date, mode), []

        transferred, sold, deficit = 0, 0, 0
        for counter in counters:
            series.append({'name': counter.name, 'data': []})
        temp = []
        for query_date in dates:
            categories.append(query_date)
            date_transfers = self.filter(date__icontains=query_date)

            for transfer in date_transfers:
                # for item in range(len(series)):
                # if series[item]['name'] == transfer.counter.name:
                total = transfer.counter_transfer_items.all().aggregate(total=models.Sum('sold'))['total']
                temp.append({
                    'date': query_date,
                    'counter': transfer.counter.name,
                    'total': total
                })

        dataset = self.values('counter__name')\
            .annotate(survived_count=models.Count('sold', filter=models.Q(trashed=True)),
                      not_survived_count=models.Count('counter', filter=models.Q(trashed=False))) \
            .order_by('counter')
        for i in dataset:
            print i
            print '*'*123
        title = self.generate_title('Counter Transfer Report ', date_from, date_to, date, mode)
        data = {
            'series': series,
            'title': title,
            'categories': categories
        }
        return data

    def highcharts_pie_filter(self, date_from=None, date_to=None, date=None, mode=None, counter=None):
        dates, items = self.get_dates(date_from, date_to, date, mode, counter), []
        transferred, sold, deficit = 0, 0, 0
        for query_date in dates:
            date_transfers = self.filter(date__icontains=query_date)

            for transfer in date_transfers:
                transferred += transfer.counter_transfer_items.all().aggregate(total=models.Sum('transferred_qty'))['total']
                sold += transfer.counter_transfer_items.all().aggregate(total=models.Sum('sold'))['total']
                deficit += transfer.counter_transfer_items.all().aggregate(total=models.Sum('deficit'))['total']
        items.append({'name': 'sold', 'y': sold})
        items.append({'name': 'deficit', 'y': deficit}),
        items.append({'name': 'transferred', 'y': transferred})
        title = self.generate_title('Counter Transfer Report ', date_from, date_to, date, mode)
        data = {
            'data': items,
            'title': title,
            'name': 'Quantity'
        }
        return data

    def all_items_filter(self, start_date=None, end_date=None):
        query = self.all()
        if start_date and end_date is not None:
            query = query.filter(
                models.Q(date__gte=start_date) &
                models.Q(date__lte=end_date)
            )
        else:
            if start_date is not None:
                query = query.filter(date__gte=start_date)
            if end_date is not None:
                query = query.filter(date__lte=end_date)
        query_dates = query.values_list('date').annotate(total_item=models.Sum('counter_transfer_items__transferred_qty'))
        categories, transferred, sold = [], [], []
        for date in query_dates:
            # query_date = list(date)[0]
            categories.append(date)
            date_transfers = self.filter(date__icontains=date)
            for transfer in date_transfers:
                transferred.append(transfer.counter_transfer_items.all().aggregate(total=models.Sum('transferred_qty'))['total'])
                sold.append(transfer.counter_transfer_items.all().aggregate(total=models.Sum('sold'))['total'])
        data = {
            'categories': categories,
            'series': [
                {'name': 'transferred', 'data': transferred},
                {'name': 'sold', 'data': sold},
            ]
        }
        # print data
        # # print [r.counter_transfer_items.values_list('quantity').annotate(total=models.Sum('quantity')) for r in query]
        # for item in query:
        #     # print item.__dict__
        #     print item.counter_transfer_items.all().aggregate(total_item=models.Sum('qty'))
        #     print item.date
        # print query

        return data

    def all_item_closed(self, instance):
        return True

    def instance_quantities(self, instance):
        return 0


class CounterTransfer(models.Model):
    counter = models.ForeignKey(Counter, on_delete=models.CASCADE, blank=True, null=True,
                                verbose_name=pgettext_lazy("CounterTransfer field", 'counter'))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='counter_transfer_users',
        verbose_name=pgettext_lazy('Sales field', 'user'))
    action = models.IntegerField(
        pgettext_lazy('Stock item field', 'action'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    name = models.CharField(
        pgettext_lazy('CounterTransfer field', 'name'), null=True, blank=True, max_length=128)
    description = models.TextField(
        verbose_name=pgettext_lazy('CounterTransfer field', 'description'), blank=True, null=True)
    updated_at = models.DateTimeField(
        pgettext_lazy('CounterTransfer field', 'updated at'), auto_now=True, null=True)
    date = models.DateField(pgettext_lazy('CounterTransfer field', 'date'),
                            default=now)
    created = models.DateTimeField(pgettext_lazy('CounterTransfer field', 'created'),
                                   default=now, editable=False)
    trashed = models.BooleanField(default=False)

    objects = TransferManager()

    class Meta:
        app_label = 'countertransfer'
        verbose_name = pgettext_lazy('CounterTransfer model', 'CounterTransfer')
        verbose_name_plural = pgettext_lazy('CounterTransfers model', 'CounterTransfers')

    def __str__(self):
        return str(self.id)

    def all_items_closed(self):
        query = self.counter_transfer_items.filter(closed=False)
        if query.exists():
            return False
        return True

    def any_closed(self):
        """ Return true if one of its transferred item is closed """
        query = self.counter_transfer_items.filter(closed=True)
        if query.exists():
            return True
        return False

    def on_post_save(self):
        pass
        # print "%s.on_post_save()" % self
        # ReportItem.objects.create_report(self)

    def on_post_delete(self):
        pass
        # print "%s.on_post_save()" % self


class TransferItemManager(BaseUserManager):
    def filter_dates(self, date_from, date_to, date, mode, counter=None):
        """
        Return distinct transfer dates between dates
        :param date_from: Date: start date for date range
        :param date_to: Date: end range
        :param date: Date: filter transfer for specific date
        :param mode: string : month, year, range
        :return: a list of dates
        """
        query = self.all()
        if counter:
            query = query.filter(counter__pk=counter)
        if date:
            year = date.split("-")[0]
            if len(date.split('-')) >= 2:
                month = date.split("-")[1]
            else:
                month = "01"
            if mode == "month":
                query = query.filter(transfer__date__year=year, transfer__date__month=month)
            elif mode == "year":
                query = query.filter(transfer__date__year=year)
            else:
                query = query.filter(transfer__date__icontains=date)
        elif date_from and date_to:
            if mode:
                year_from = date_from.split("-")[0]
                if len(date_from.split('-')) >= 2:
                    month_from = date_from.split("-")[1]
                else:
                    month_from = "01"

                year_to = date_to.split("-")[0]
                if len(date_to.split('-')) >= 2:
                    month_to = date_to.split("-")[1]
                else:
                    month_to = "01"

                if mode == "month":
                    query = query.filter(transfer__date__year__gte=year_from,
                                         transfer__date__month__gte=month_from,
                                         transfer__date__year__lte=year_to,
                                         transfer__date__month__lte=month_to)
                elif mode == "year":
                    query = query.filter(transfer__date__year__gte=year_from,
                                         transfer__date__year__lte=year_to)
                else:
                    query = query.filter(transfer__date__range=[date_from, date_to])
            else:
                query = query.filter(transfer__date__range=[date_from, date_to])
        return query

    def temp_line(self):
        dataset = self.values('counter__name') \
            .annotate(
                price=models.Sum('total'),
                sold=models.Sum('sold'),
                transferred=models.Sum('transferred_qty')) \
            .order_by('counter')
        for i in dataset:
            print i
            print '*' * 123
        return dataset

    def top_products(self, date_from=None, date_to=None, date=None, mode=None, counter=None, query_type='total'):
        query = self.filter_dates(date_from, date_to, date, mode, counter)
        if query_type == 'sold':
            top_records = query.values('sku', 'productName').annotate(
                c=models.Count('sku', distinct=True))\
                .annotate(models.Sum('total'))\
                .annotate(models.Sum('sold')
            ).order_by('-sold__sum')
            data_item = 'sold__sum'
        elif query_type == 'total':
            top_records = query.values('sku', 'productName').annotate(
                c=models.Count('sku', distinct=True))\
                .annotate(models.Sum('total'))\
                .annotate(models.Sum('sold')
            ).order_by('-total__sum')
            data_item = 'total__sum'
        else:
            top_records = query.values('sku', 'productName').annotate(
                c=models.Count('sku', distinct=True)) \
                .annotate(models.Sum('total')) \
                .annotate(models.Sum('sold')
                          ).order_by('-total__sum')
            data_item = 'total__sum'
        categories, series = [], []
        for item in top_records:
            categories.append(str(item.get('productName')) + '-' + str(item.get('sku')))
            series.append(item.get(data_item))

        data = {
            'series': [{'name': 'Categories', 'data': series}],
            'categories': categories
        }
        return data

    def carry_forward_quantity(self, stock):
        query = self.get_queryset().filter(stock=stock)
        query = query.filter(closed=True)
        total_qty = 0
        for item in query:
            total_qty = int(total_qty) + int(item.qty)
        return total_qty

    def decrease_stock(self, instance, quantity):
        instance.sold = models.F('sold') + quantity
        instance.qty = models.F('qty') - quantity
        instance.expected_qty = instance.qty
        instance.save(update_fields=['sold', 'qty', 'expected_qty'])

    def increase_stock(self, instance, quantity):
        instance.qty = models.F('qty') + quantity
        instance.sold = models.F('sold') - quantity
        instance.expected_qty = instance.qty
        instance.save(update_fields=['qty', 'sold', 'expected_qty'])

    def instance_quantities(self, instance, filter_type='transfer', counter=None):
        if filter_type == 'transfer':
            query = self.get_queryset().filter(transfer=instance)
        else:
            query = self.get_queryset().filter(stock=instance)
        if counter:
            query = query.filter(counter=counter)
        query = query.filter(trashed=False)
        qty = query.aggregate(models.Sum('transferred_qty'))['transferred_qty__sum']
        return qty

    def instance_qty(self, instance, filter_type='transfer', counter=None):
        if filter_type == 'transfer':
            query = self.get_queryset().filter(transfer=instance)
        else:
            query = self.get_queryset().filter(stock=instance)
        if counter:
            query = query.filter(counter=counter)
        query = query.filter(trashed=False).filter(transfer__trashed=False)
        qty = query.aggregate(models.Sum('qty'))['qty__sum']
        return qty

    def instance_sold_quantity(self, instance, filter_type='transfer', counter=None):
        if filter_type == 'transfer':
            query = self.get_queryset().filter(transfer=instance)
        else:
            query = self.get_queryset().filter(stock=instance)
        if counter:
            query = query.filter(counter=counter)
        qty = query.aggregate(models.Sum('sold'))['sold__sum']
        return qty

    def instance_worth(self, instance, filter_type='transfer'):
        if filter_type == 'transfer':
            query = self.get_queryset().filter(transfer=instance)
        else:
            query = self.get_queryset().filter(stock=instance)
        total = 0
        for i in query:
            total += Decimal(i.transferred_qty) * Decimal(i.stock.cost_price.gross)
        return total

    def instance_sold_price(self, instance, filter_type='transfer'):
        if filter_type == 'transfer':
            query = self.get_queryset().filter(transfer=instance)
        else:
            query = self.get_queryset().filter(stock=instance)
        total = 0
        for i in query:
            total += Decimal(i.sold) * Decimal(i.price)
        return total

    def all_items_filter(self, start_date=None, end_date=None):
        query = self.all()
        if start_date and end_date is not None:
            query = query.filter(
                models.Q(transfer__date__gte=start_date) &
                models.Q(transfer__date__lte=end_date)
            )
        else:
            if start_date is not None:
                query = query.filter(transfer__date__gte=start_date)
            if end_date is not None:
                query = query.filter(transfer__date__lte=end_date)
        # query = query.values_list('transfer').annotate(total_item=models.Sum('transferred_qty'))
        return query


class CounterTransferItems(models.Model):
    transfer = models.ForeignKey(
        CounterTransfer, on_delete=models.CASCADE, related_name='counter_transfer_items',
        verbose_name=pgettext_lazy("CounterTransfer field", 'counter'))
    counter = models.ForeignKey(Counter, on_delete=models.CASCADE, related_name="item_counter", blank=True, null=True,
                                verbose_name=pgettext_lazy("CounterTransfer field", 'counter'))
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, blank=True, null=True,
                              verbose_name=pgettext_lazy("CounterTransfer field", 'stock'))
    quantity = models.IntegerField(
        pgettext_lazy('Stock item field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    sku = models.CharField(max_length=60, blank=True, null=True,
                           verbose_name=pgettext_lazy('CounterTransfer field', 'sku'))
    product_category = models.CharField(max_length=60, blank=True, null=True,
                                        verbose_name=pgettext_lazy('CounterTransfer field', 'category'))
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0),
                                verbose_name=pgettext_lazy('CounterTransfer field', 'price'))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0),
                                     verbose_name=pgettext_lazy('CounterTransfer field', 'unit price'))

    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0),
                              verbose_name=pgettext_lazy('CounterTransfer field', 'tax'))
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0),
                                   verbose_name=pgettext_lazy('CounterTransfer field', 'discount'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0),
                                verbose_name=pgettext_lazy('CounterTransfer field', 'total price'))

    qty = models.PositiveIntegerField(default=1,
                                      verbose_name=pgettext_lazy('CounterTransfer field', 'quantity'))
    transferred_qty = models.PositiveIntegerField(default=1,
                                                  verbose_name=pgettext_lazy('CounterTransfer field', 'transferred_qty'))
    deficit = models.IntegerField(default=0,
                                          verbose_name=pgettext_lazy('CounterTransfer field', 'deficit'))
    expected_qty = models.PositiveIntegerField(default=1,
                                               verbose_name=pgettext_lazy('CounterTransfer field', 'expected_qty'))

    sold = models.PositiveIntegerField(default=0,
                                       verbose_name=pgettext_lazy('CounterTransfer field', 'sold'))

    productName = models.CharField(max_length=100, blank=True, null=True,
                                   verbose_name=pgettext_lazy('CounterTransfer field', 'product name'))
    description = models.TextField(
        verbose_name=pgettext_lazy('CounterTransfer field', 'description'), blank=True, null=True)
    updated_at = models.DateTimeField(
        pgettext_lazy('CounterTransfer field', 'updated at'), auto_now=True, null=True)
    created = models.DateTimeField(pgettext_lazy('CounterTransfer field', 'created'),
                                   default=now, editable=False)
    closed = models.BooleanField(default=False)
    trashed = models.BooleanField(default=False)
    objects = TransferItemManager()

    class Meta:
        app_label = 'countertransfer'
        verbose_name = pgettext_lazy('CounterTransfer model', 'CounterTransfer')
        verbose_name_plural = pgettext_lazy('CounterTransfers model', 'CounterTransfers')

    def __str__(self):
        return str(self.sku) + ' ' + str(self.qty)

    def save(self, *args, **kwargs):
        try:
            self.total = self.qty * self.price
            super(CounterTransferItems, self).save(*args, **kwargs)
        except Exception as e:
            print(e)
            pass



@receiver(signals.post_save)
def search_on_post_save(sender, instance, **kwargs):
    if issubclass(sender, CounterTransfer):
        instance.on_post_save()


@receiver(signals.post_delete)
def search_on_post_delete(sender, instance, **kwargs):
    if issubclass(sender, CounterTransfer):
         instance.on_post_delete()



