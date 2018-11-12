from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
from ...sale.models import Sales, SoldItem

from structlog import get_logger

logger = get_logger(__name__)


def get_hours_results(date, h):
    try:
        sales_at_date = Sales.objects.filter(created__contains=date)
        sales_at_h = sales_at_date.extra(where=['extract(hour from created) in (' + str(h - 3) + ')'])
        try:
            amount = sales_at_h.aggregate(Sum('total_net'))['total_net__sum']
            if amount is not None:
                return amount
            else:
                amount = 0
                return amount
        except ObjectDoesNotExist:
            amount = 0
            return amount
    except ObjectDoesNotExist:
        amount = 0
        return amount


def get_hours_results_range(date_from, date_to, l, h):
    try:
        sales_at_date = Sales.objects.filter(created__range=[date_from, date_to])
        sales_at_h = sales_at_date.filter(created__hour__range=[l, h])
        try:
            amount = Sales.objects.filter(pk__in=sales_at_h).aggregate(Sum('total_net'))['total_net__sum']
            if amount is not None:
                return amount
            else:
                amount = 0
                return amount
        except ObjectDoesNotExist:
            amount = 0
            return amount
    except ObjectDoesNotExist:
        amount = 0
        return amount


def get_date_results_range(date_from, date_to):
    try:
        sales_at_date = Sales.objects.filter(created__range=[date_from, date_to])
        try:
            amount = Sales.objects.filter(pk__in=sales_at_date).aggregate(Sum('total_net'))['total_net__sum']
            if amount is not None:
                return amount
            else:
                amount = 0
                return amount
        except ObjectDoesNotExist:
            amount = 0
            return amount
    except ObjectDoesNotExist:
        amount = 0
        return amount


def get_date_results(date):
    try:
        sales_at_date = Sales.objects.filter(created__contains=date)
        try:
            amount = Sales.objects.filter(pk__in=sales_at_date).aggregate(Sum('total_net'))['total_net__sum']
            if amount is not None:
                return amount
            else:
                amount = 0
                return amount
        except ObjectDoesNotExist:
            amount = 0
            return amount
    except ObjectDoesNotExist:
        amount = 0
        return amount


def get_category_results(category, year, month):
    try:
        amount = SoldItem.objects.filter(product_category__contains=category, sales__created__year=year,
                                         sales__created__month=month).aggregate(Sum('total_cost'))['total_cost__sum']
        if amount is not None:
            return amount
        else:
            amount = 0
            return amount
    except ObjectDoesNotExist:
        amount = 0
        return amount


def get_item_results(item, year, month):
    try:
        amount = SoldItem.objects.filter(product_name__contains=item, sales__created__year=year,
                                         sales__created__month=month).aggregate(Sum('total_cost'))['total_cost__sum']
        if amount is not None:
            return amount
        else:
            amount = 0
            return amount
    except ObjectDoesNotExist:
        amount = 0
        return amount


def get_user_results(user, year, month):
    try:
        amount = Sales.objects.filter(user__name__contains=user, created__year=year, created__month=month).aggregate(
            Sum('total_net'))['total_net__sum']
        if amount is not None:
            return amount
        else:
            amount = 0
            return amount
    except ObjectDoesNotExist:
        amount = 0
        return amount


def get_terminal_results(terminal, year, month):
    try:
        amount = Sales.objects.filter(terminal__terminal_name__contains=terminal, created__year=year,
                                      created__month=month).aggregate(Sum('total_net'))['total_net__sum']
        if amount is not None:
            return amount
        else:
            amount = 0
            return amount
    except ObjectDoesNotExist:
        amount = 0
        return amount
