from django.contrib.admin.views.decorators import \
    staff_member_required as _staff_member_required
from django.template.response import TemplateResponse
from payments import PaymentStatus
from ..order.models import Order, Payment
from ..order import OrderStatus
from ..sale.models import Sales, SoldItem
from ..product.models import Category, Stock
from ..credit.models import Credit
from django.db.models import Count, Sum
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from .reports.hours_chart import get_item_results, get_category_results
from django.utils.dateformat import DateFormat
from decimal import Decimal
import datetime
import logging
import random
import calendar
import dateutil.relativedelta


debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


def staff_member_required(f):
    return _staff_member_required(f, login_url='home')

@staff_member_required
def index(request):
    month = request.GET.get('month')
    year = request.GET.get('year')
    period = request.GET.get('period')

    try:
        last_sale = Sales.objects.latest('id')
        date = DateFormat(last_sale.created).format('Y-m-d')
    except:
        date = DateFormat(datetime.datetime.today()).format('Y-m-d')

    try:
        orders_to_ship = Order.objects.filter(status=OrderStatus.FULLY_PAID)
        orders_to_ship = (orders_to_ship
                          .select_related('user')
                          .prefetch_related('groups', 'groups__items', 'payments'))
        payments = Payment.objects.filter(
            status=PaymentStatus.PREAUTH).order_by('-created')
        payments = payments.select_related('order', 'order__user')
        #top categories
        if period:
            cat = top_categories(month, year, period)
        else:
            cat = top_categories()
        items = top_items()
        low_stock_order = dashbord_get_low_stock_products()


        try:
            startYear = Sales.objects.all().first().created.year
            startMonth = Sales.objects.all().first().created.month
        except:
            startYear = datetime.datetime.today().year
            startMonth = datetime.datetime.today().month

        ctx = {'preauthorized_payments': payments,
               'orders_to_ship': orders_to_ship,
               'low_stock': low_stock_order['low_stock'],
               'pn':low_stock_order['pn'],
               'sz': low_stock_order['sz'],
               'gid': low_stock_order['gid'],
               #top_cat
               "sales_by_category": cat['sales_by_category'],
               "categs": cat['categs'],
               "avg": cat['avg'],
               "labels": cat['labels'],
               "default": cat['default'],
               "hcateg": cat['hcateg'],
               "date_total_sales": cat['date_total_sales'],
               "no_of_customers": cat['no_of_customers'],
               "date_period": cat['date_period'],

               #items
               "sales_by_item": items['sales_by_item'],
               "items": items['items'],
               "items_avg": items['items_avg'],
               "items_labels": items['items_labels'],
               "items_default": items['items_default'],
               "items_hcateg": items['items_hcateg'],
               "highest_item": items['highest_item'],
               "lowest_item": items['lowest_item'],
               'startYear': startYear,
               'startMonth': startMonth,
               }
        if period:
            return TemplateResponse(request, 'dashboard/ajax.html', ctx)
        else:
            return TemplateResponse(request, 'dashboard/index.html', ctx)
    except BaseException as e:
        if period:
            return TemplateResponse(request, 'dashboard/ajax.html', {"e":e, "date":date})
        else:
            return TemplateResponse(request, 'dashboard/index.html', {"e":e, "date":date})

@staff_member_required
def landing_page(request):
    ctx = {}
    return TemplateResponse(request, 'dashboard/landing-page.html', ctx)


def top_categories(month=None, year=None, period=None):
    today = datetime.datetime.now()
    try:
        last_sale = Sales.objects.latest('id')
        date = DateFormat(last_sale.created).format('Y-m-d')
    except:
        date = DateFormat(datetime.datetime.today()).format('Y-m-d')

    if year and month:
        if len(str(month)) == 1:
            m = '0' + str(month)
            fdate = str(year) + '-' + m
        else:
            fdate = str(year) + '-' + str(month)

        d = datetime.datetime.strptime(fdate, "%Y-%m")

    if period == 'year':
        lastyear = d - dateutil.relativedelta.relativedelta(years=1)
        y = str(lastyear.strftime("%Y"))
        month = str(datetime.datetime.strptime(month, "%m").strftime("%m"))
        sales_by_category = SoldItem.objects.filter(sales__created__year__range=[y, year], sales__created__month__lte=month
                                                    ).values('product_category'
                                                    ).annotate(c=Count('product_category', distinct=True)
                                                    ).annotate(Sum('total_cost')
                                                    ).annotate(Sum('quantity')).order_by('-quantity__sum')[:5]
        sales_customers = Sales.objects.filter(created__year__range=[y, year], created__month__lte=month).count()
        credit_customers = Credit.objects.filter(created__year__range=[y, year], created__month__lte=month).count()

        date_period = str(lastyear.strftime("%B"))+'/'+str(lastyear.strftime("%Y"))+' - '+str(datetime.datetime.strptime(month, "%m").strftime("%B"))+'/'+ str(year)
    elif period == 'month':
        sales_by_category = SoldItem.objects.filter(sales__created__year=str(d.strftime("%Y")), sales__created__month=str(d.strftime("%m"))
                                                    ).values('product_category'
                                                    ).annotate(c=Count('product_category', distinct=True)
                                                    ).annotate(Sum('total_cost')
                                                    ).annotate(Sum('quantity')).order_by('-quantity__sum')[:5]
        sales_customers = Sales.objects.filter(created__year=str(d.strftime("%Y")), created__month=str(d.strftime("%m"))).count()
        credit_customers = Credit.objects.filter(created__year=str(d.strftime("%Y")), created__month=str(d.strftime("%m"))).count()
        date_period = str(datetime.datetime.strptime(month, "%m").strftime("%B")) + '/' + str(datetime.datetime.strptime(year, "%Y").strftime("%Y"))

    elif period == 'quarter':
        p = d - dateutil.relativedelta.relativedelta(months=3)
        month = str(datetime.datetime.strptime(month, "%m").strftime("%m"))
        sales_by_category = SoldItem.objects.filter(sales__created__year=str(p.strftime("%Y")),
                                                    sales__created__month__range=[str(p.strftime("%m")), month]
                                                    ).values('product_category'
                                                    ).annotate(c=Count('product_category', distinct=True)
                                                    ).annotate(Sum('total_cost')
                                                    ).annotate(Sum('quantity')).order_by('-quantity__sum')[:5]
        sales_customers = Sales.objects.filter(created__year=str(p.strftime("%Y")),
                                                    created__month__range=[str(p.strftime("%m")), month]).count()
        credit_customers = Credit.objects.filter(created__year=str(p.strftime("%Y")),
                                                    created__month__range=[str(p.strftime("%m")), month]).count()
        date_period = str(p.strftime("%B")) + '/' + str(p.strftime("%Y")) + ' - ' + str(
            datetime.datetime.strptime(month, "%m").strftime("%B")) + '/' + str(year)

    else:
        sales_by_category = SoldItem.objects.filter(sales__created__contains=date).values('product_category').annotate(
            c=Count('product_category', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
            '-quantity__sum')[:5]
        sales_customers = Sales.objects.filter(created__contains=date).count()
        credit_customers = Credit.objects.filter(created__contains=date).count()
        date_period = date

    try:
        sales_by_category = sales_by_category
        quantity_totals = sales_by_category.aggregate(Sum('quantity__sum'))['quantity__sum__sum']
        new_sales = []
        for sales in sales_by_category:
            color = "#%03x" % random.randint(0, 0xFFF)
            sales['color'] = color
            percent = (Decimal(sales['quantity__sum']) / Decimal(quantity_totals)) * 100
            percentage = round(percent, 2)
            sales['percentage'] = percentage
            for s in range(0, sales_by_category.count(), 1):
                sales['count'] = s
            new_sales.append(sales)
            sales['total_cost'] = int(sales['total_cost__sum'])
        categs = Category.objects.all()
        this_year = today.year
        avg_m = Sales.objects.filter(created__year=this_year).annotate(c=Count('total_net'))
        highest_category_sales = new_sales[0]['product_category']
        default = []
        labels = []
        for i in range(1, (today.month + 1), 1):
            if len(str(i)) == 1:
                m =  str('0' + str(i))
            else:
                m = str(i)
            amount = get_category_results(highest_category_sales, str(today.year), m)
            labels.append(calendar.month_name[int(m)][0:3])
            default.append(amount)

        date_total_sales = Sales.objects.filter(created__contains=date).aggregate(Sum('total_net'))[
            'total_net__sum']

        try:
            sales_customers = sales_customers
            credit_customers = credit_customers
        except:
            sales_customers = 0
            credit_customers = 0
        no_of_customers = sales_customers + credit_customers

        data = {
            "sales_by_category": new_sales,
            "categs": categs,
            "avg": avg_m,
            "labels": labels,
            "default": default,
            "hcateg": highest_category_sales,
            "date_total_sales": date_total_sales,
            "no_of_customers":no_of_customers,
            "date_period":date_period
        }
        return data
    except Exception,e:
        error_logger.error(e)
        data = {
            "sales_by_category": None,
            "categs": None,
            "avg": None,
            "labels": None,
            "default": None,
            "hcateg": None,
            "date_total_sales": None,
            "no_of_customers": None,
        }
        return data

def top_items(month=None, year=None, period=None):
    today = datetime.datetime.now()
    try:
        last_sale = Sales.objects.latest('id')
        date = DateFormat(last_sale.created).format('Y-m-d')
    except:
        date = DateFormat(datetime.datetime.today()).format('Y-m-d')

    if year and month:
        if len(str(month)) == 1:
            m = '0' + str(month)
            fdate = str(year) + '-' + m
        else:
            fdate = str(year) + '-' + str(month)

        d = datetime.datetime.strptime(fdate, "%Y-%m")

    if period == 'year':
        lastyear = d - dateutil.relativedelta.relativedelta(years=1)
        y = str(lastyear.strftime("%Y"))
        month = str(datetime.datetime.strptime(month, "%m").strftime("%m"))
        sales_by_category = SoldItem.objects.filter(sales__created__year__range=[y, year], sales__created__month__lte=month).values(
                                                        'product_name').annotate(
                                                        c=Count('product_name', distinct=True)).annotate(
                                                        Sum('total_cost')).annotate(Sum('quantity')).order_by(
                                                        '-quantity__sum')[:5]
        highest_item = SoldItem.objects.filter(sales__created__year__range=[y, year], sales__created__month__lte=month).values(
                                                   'product_name').annotate(
                                                   c=Count('product_name', distinct=False)).annotate(
                                                   Sum('total_cost')).annotate(Sum('quantity')).order_by(
                                                   '-quantity__sum')[:1]
        lowest_item = SoldItem.objects.filter(sales__created__year__range=[y, year], sales__created__month__lte=month).values('product_name').annotate(
            c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
            'quantity__sum', 'total_cost__sum')[:1]

    elif period == 'month':
        sales_by_category = SoldItem.objects.filter(sales__created__year=str(d.strftime("%Y")), sales__created__month=str(d.strftime("%m"))).values('product_name').annotate(
            c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
            '-quantity__sum')[:5]

        highest_item = SoldItem.objects.filter(sales__created__year=str(d.strftime("%Y")), sales__created__month=str(d.strftime("%m"))).values('product_name').annotate(
            c=Count('product_name', distinct=False)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
            '-quantity__sum')[:1]
        lowest_item = SoldItem.objects.filter(sales__created__year=str(d.strftime("%Y")), sales__created__month=str(d.strftime("%m"))).values('product_name').annotate(
            c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
            'quantity__sum', 'total_cost__sum')[:1]

    elif period == 'quarter':
        p = d - dateutil.relativedelta.relativedelta(months=3)
        month = str(datetime.datetime.strptime(month, "%m").strftime("%m"))
        sales_by_category = SoldItem.objects.filter(sales__created__year=str(p.strftime("%Y")),
                                                    sales__created__month__range=[str(p.strftime("%m")), month]).values('product_name').annotate(
            c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
            '-quantity__sum')[:5]
        highest_item = SoldItem.objects.filter(sales__created__year=str(p.strftime("%Y")),
                                                    sales__created__month__range=[str(p.strftime("%m")), month]).values('product_name').annotate(
            c=Count('product_name', distinct=False)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
            '-quantity__sum')[:1]
        lowest_item = SoldItem.objects.filter(sales__created__year=str(p.strftime("%Y")),
                                                    sales__created__month__range=[str(p.strftime("%m")), month]).values('product_name').annotate(
            c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
            'quantity__sum', 'total_cost__sum')[:1]

    else:
        sales_by_category = SoldItem.objects.filter(sales__created__contains=date).values('product_name').annotate(
            c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
            '-quantity__sum')[:5]
        highest_item = SoldItem.objects.filter(sales__created__contains=date).values('product_name').annotate(
            c=Count('product_name', distinct=False)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
            '-quantity__sum')[:1]
        lowest_item = SoldItem.objects.filter(sales__created__contains=date).values('product_name').annotate(
            c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
            'quantity__sum', 'total_cost__sum')[:1]

    try:
        sales_by_category = sales_by_category
        highest_item = highest_item
        lowest_item = lowest_item
        sales_by_category_totals = sales_by_category.aggregate(Sum('quantity__sum'))['quantity__sum__sum']
        new_sales = []
        for sales in sales_by_category:
            color = "#%03x" % random.randint(0, 0xFFF)
            sales['color'] = color
            percent = (Decimal(sales['quantity__sum']) / Decimal(sales_by_category_totals)) * 100
            percentage = round(percent, 2)
            sales['percentage'] = percentage
            for s in range(0, sales_by_category.count(), 1):
                sales['count'] = s
            new_sales.append(sales)
        categs = SoldItem.objects.values('product_name').annotate(Count('product_name', distinct=True)).order_by()
        this_year = today.year
        avg_m = Sales.objects.filter(created__year=this_year).annotate(c=Count('total_net'))
        highest_category_sales = new_sales[0]['product_name']
        default = []
        labels = []
        for i in range(1, (today.month + 1), 1):
            if len(str(i)) == 1:
                m = str('0' + str(i))
            else:
                m = str(i)
            amount = get_item_results(highest_category_sales, str(today.year), m)
            labels.append(calendar.month_name[int(m)][0:3])
            default.append(amount)

        data = {
            "sales_by_item": new_sales,
            "items": categs,
            "items_avg": avg_m,
            "items_labels": labels,
            "items_default": default,
            "items_hcateg": highest_category_sales,
            "highest_item":highest_item,
            "lowest_item":lowest_item,
        }
        return data
    except IndexError as e:
        error_logger.error(e)
        data = {
            "sales_by_item": None,
            "items": None,
            "items_avg": None,
            "items_labels": None,
            "items_default": None,
            "items_hcateg": None,
            "highest_item": None,
            "lowest_item": None,
        }
        return data


@staff_member_required
def styleguide(request):
    return TemplateResponse(request, 'dashboard/styleguide/index.html', {})

def dashbord_get_low_stock_products():
    products = Stock.objects.get_low_stock().order_by('-id')
    paginator = Paginator(products, 10)
    try:
        low_stock = paginator.page(1)
    except PageNotAnInteger:
        low_stock = paginator.page(1)
    except InvalidPage:
        low_stock = paginator.page(1)
    except EmptyPage:
        low_stock = paginator.page(paginator.num_pages)
    data = {'low_stock': low_stock, 'pn': paginator.num_pages, 'sz': 10, 'gid': 0}
    return data

def get_low_stock_products():
    products = Stock.objects.get_low_stock()
    return products
