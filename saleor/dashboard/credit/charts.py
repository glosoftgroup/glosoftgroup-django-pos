from django.template.response import TemplateResponse
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Sum
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
import datetime
from datetime import timedelta
from django.utils.dateformat import DateFormat
import logging
import random
from decimal import Decimal
from calendar import monthrange
import calendar

import re
from ..views import staff_member_required
from ...sale.models import Sales, SoldItem, Terminal
from ...product.models import Category
from ...decorators import permission_decorator
from ...utils import render_to_pdf

from .hours_chart import get_item_results, get_terminal_results, get_user_results, get_hours_results, \
    get_hours_results_range, get_date_results_range, get_date_results, get_category_results

from structlog import get_logger

logger = get_logger(__name__)


@staff_member_required
def sales_category_chart(request, image=None):
    get_date = request.GET.get('date')
    today = datetime.datetime.now()
    if get_date:
        date = get_date
    else:
        try:
            last_sale = Sales.objects.latest('id')
            date = DateFormat(last_sale.created).format('Y-m-d')
        except:
            date = DateFormat(datetime.datetime.today()).format('Y-m-d')

    if image:
        dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
        ImageData = image
        ImageData = dataUrlPattern.match(ImageData).group(2)

        sales_by_category = SoldItem.objects.filter(sales__created__contains=date).values('product_category').annotate(
            c=Count('product_category', distinct=True)).annotate(Sum('total_cost')).order_by('-total_cost__sum')[:5]
        sales_by_category_totals = sales_by_category.aggregate(Sum('total_cost__sum'))['total_cost__sum__sum']
        new_sales = []
        for sales in sales_by_category:
            color = "#%03x" % random.randint(0, 0xFFF)
            sales['color'] = color
            percent = (Decimal(sales['total_cost__sum']) / Decimal(sales_by_category_totals)) * 100
            percentage = round(percent, 2)
            sales['percentage'] = percentage
            for s in range(0, sales_by_category.count(), 1):
                sales['count'] = s
            new_sales.append(sales)

        data = {
            'today': last_sale.created,
            'sales_by_category': new_sales,
            'puller': request.user,
            'image': ImageData,
        }
        pdf = render_to_pdf('dashboard/reports/sales/charts/pdf/category_pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')

    if date:
        try:
            sales_by_category = SoldItem.objects.filter(sales__created__contains=date).values(
                'product_category').annotate(
                c=Count('product_category', distinct=True)).annotate(Sum('total_cost')).order_by('-total_cost__sum')[:5]
            sales_by_category_totals = sales_by_category.aggregate(Sum('total_cost__sum'))['total_cost__sum__sum']
            new_sales = []
            for sales in sales_by_category:
                color = "#%03x" % random.randint(0, 0xFFF)
                sales['color'] = color
                percent = (Decimal(sales['total_cost__sum']) / Decimal(sales_by_category_totals)) * 100
                percentage = round(percent, 2)
                sales['percentage'] = percentage
                for s in range(0, sales_by_category.count(), 1):
                    sales['count'] = s
                new_sales.append(sales)
            categs = Category.objects.all()
            this_year = today.year
            avg_m = Sales.objects.filter(created__year=this_year).annotate(c=Count('total_net'))
            highest_category_sales = new_sales[0]['product_category']
            default = []
            labels = []
            for i in range(1, (today.month + 1), 1):
                if len(str(i)) == 1:
                    m = str('0' + str(i))
                else:
                    m = str(i)
                amount = get_category_results(highest_category_sales, str(today.year), m)
                labels.append(calendar.month_name[int(m)][0:3])
                default.append(amount)

            data = {
                "sales_by_category": new_sales,
                "categs": categs,
                "avg": avg_m,
                "labels": labels,
                "default": default,
                "hcateg": highest_category_sales,
                "sales_date": date
            }
            return TemplateResponse(request, 'dashboard/reports/sales/ajax/category.html', data)
        except ObjectDoesNotExist as e:
            return TemplateResponse(request, 'dashboard/reports/sales/ajax/category.html', {"e": e, "date": date})
        except IndexError as e:
            return TemplateResponse(request, 'dashboard/reports/sales/ajax/category.html', {"e": e, "date": date})


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def get_category_sale_details(request):
    get_categ = request.GET.get('category')
    today = datetime.datetime.now()
    if get_categ:
        try:
            """ this year """
            this_year_sales = \
            SoldItem.objects.filter(product_category__contains=get_categ, sales__created__year=today.year
                                    ).aggregate(Sum('total_cost'))['total_cost__sum']
            y_sales = SoldItem.objects.filter(sales__created__year=today.year).aggregate(Sum('total_cost'))[
                'total_cost__sum']
            try:
                ty_percent = round((Decimal(this_year_sales) / Decimal(y_sales)) * 100, 2)
                ty_others = 100 - ty_percent
            except:
                ty_percent = 0
                ty_others = 0

            """ this month """
            this_month_sales = \
            SoldItem.objects.filter(product_category__contains=get_categ, sales__created__year=today.year,
                                    sales__created__month=today.month).aggregate(Sum('total_cost'))['total_cost__sum']
            m_sales = \
            SoldItem.objects.filter(sales__created__year=today.year, sales__created__month=today.month).aggregate(
                Sum('total_cost'))['total_cost__sum']
            try:
                tm_percent = round((Decimal(this_month_sales) / Decimal(m_sales)) * 100, 2)
                tm_others = 100 - tm_percent
            except:
                tm_percent = 0
                tm_others = 0

            """ last year """
            last_year_sales = \
            SoldItem.objects.filter(product_category__contains=get_categ, sales__created__year=(today.year - 1)
                                    ).aggregate(Sum('total_cost'))['total_cost__sum']
            ly_sales = SoldItem.objects.filter(sales__created__year=(today.year - 1)).aggregate(Sum('total_cost'))[
                'total_cost__sum']
            try:
                ly_percent = round((Decimal(last_year_sales) / Decimal(ly_sales)) * 100, 2)
                ly_others = 100 - ly_percent
            except:
                ly_percent = 0
                ly_others = 0

            """ last month """
            last_month = today.month - 1 if today.month > 1 else 12
            last_month_sales = \
            SoldItem.objects.filter(product_category__contains=get_categ, sales__created__year=today.year,
                                    sales__created__month=last_month).aggregate(Sum('total_cost'))['total_cost__sum']

            lm_sales = \
            SoldItem.objects.filter(sales__created__year=today.year, sales__created__month=last_month).aggregate(
                Sum('total_cost'))['total_cost__sum']
            try:
                lm_percent = round((Decimal(last_month_sales) / Decimal(lm_sales)) * 100, 2)
                lm_others = 100 - lm_percent
            except:
                lm_percent = 0
                lm_others = 0
            last_sales = SoldItem.objects.filter(product_category__contains=get_categ).values('product_category',
                                                                                              'total_cost',
                                                                                              'sales__created').annotate(
                Sum('total_cost', distinct=True)).order_by().latest('sales__id')

            data = {
                "category": get_categ,
                "this_year_sales": this_year_sales,
                "this_month_sales": this_month_sales,
                "last_year_sales": last_year_sales,
                "last_month_sales": last_month_sales,
                "ty_percent": ty_percent,
                "ty_others": ty_others,
                "tm_percent": tm_percent,
                "tm_others": tm_others,
                "ly_percent": ly_percent,
                "ly_others": ly_others,
                "lm_percent": lm_percent,
                "lm_others": lm_others,
                "last_sales": last_sales
            }
            return TemplateResponse(request, 'dashboard/reports/sales/charts/by_category.html', data)
        except ObjectDoesNotExist as e:
            return TemplateResponse(request, 'dashboard/reports/sales/charts/by_category.html', {})
        # return HttpResponse(e)


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def sales_date_chart(request, image=None):
    get_date = request.GET.get('date')
    if get_date:
        date = get_date
    else:
        try:
            last_sale = Sales.objects.latest('id')
            date = DateFormat(last_sale.created).format('Y-m-d')
        except:
            date = DateFormat(datetime.datetime.today()).format('Y-m-d')

    if image:
        dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
        ImageData = image
        ImageData = dataUrlPattern.match(ImageData).group(2)

        date_total_sales = Sales.objects.filter(created__contains=date).aggregate(Sum('total_net'))['total_net__sum']
        users = Sales.objects.values('user__email', 'user__name', 'terminal__terminal_name').annotate(
            Count('user')).annotate(
            Sum('total_net')).order_by().filter(created__contains=date)
        data = {
            'today': last_sale.created,
            'users': users,
            'puller': request.user,
            'image': ImageData,
            "date_total_sales": date_total_sales,
        }
        pdf = render_to_pdf('dashboard/reports/sales/charts/pdf/pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')

    if date:
        try:
            td_sales = Sales.objects.filter(created__contains=date).order_by('-id')[:1]
            if td_sales:
                for dt in td_sales:
                    seld = dt.created
                selected_sales_date = DateFormat(seld).format('jS F Y')
            else:
                selected_sales_date = date
            prev_sales = Sales.objects.filter(created__lte=date)[:1]
            if prev_sales:
                for dt in prev_sales:
                    prevd = dt.created
                prevdate = DateFormat(prevd).format('Y-m-d')
                previous_sales_date = DateFormat(prevd).format('jS F Y')
            else:
                prevdate = date
                previous_sales_date = selected_sales_date

            no_of_customers = Sales.objects.filter(created__contains=date).count()
            prevno_of_customers = Sales.objects.filter(created__contains=prevdate).count()
            try:
                customer_diff = int(
                    ((Decimal(no_of_customers) - Decimal(prevno_of_customers)) / Decimal(prevno_of_customers)) * 100)
            except:
                customer_diff = 0

            date_total_sales = Sales.objects.filter(created__contains=date).aggregate(Sum('total_net'))[
                'total_net__sum']
            prevdate_total_sales = Sales.objects.filter(created__contains=prevdate).aggregate(Sum('total_net'))[
                'total_net__sum']
            try:
                sales_diff = int(
                    ((Decimal(date_total_sales) - Decimal(prevdate_total_sales)) / Decimal(prevdate_total_sales)) * 100)
            except:
                sales_diff = 0
            items = SoldItem.objects.filter(sales__created__icontains=date)

            # that date
            seven_eight = get_hours_results(date, 7, 8)
            eight_nine = get_hours_results(date, 8, 9)
            nine_ten = get_hours_results(date, 9, 10)
            ten_eleven = get_hours_results(date, 10, 11)
            eleven_twelve = get_hours_results(date, 11, 12)
            twelve_thirteen = get_hours_results(date, 12, 13)
            thirteen_fourteen = get_hours_results(date, 13, 14)
            fourteen_fifteen = get_hours_results(date, 14, 15)
            fifteen_sixteen = get_hours_results(date, 15, 16)
            sixteen_seventeen = get_hours_results(date, 16, 17)
            seventeen_eighteen = get_hours_results(date, 17, 18)
            eighteen_nineteen = get_hours_results(date, 18, 19)
            nineteen_twenty = get_hours_results(date, 19, 20)
            twenty_twentyone = get_hours_results(date, 20, 21)
            twentyone_twentytwo = get_hours_results(date, 21, 22)

            default = [seven_eight, eight_nine, nine_ten, ten_eleven,
                       eleven_twelve, twelve_thirteen, thirteen_fourteen, fourteen_fifteen,
                       fifteen_sixteen, sixteen_seventeen, seventeen_eighteen,
                       eighteen_nineteen, nineteen_twenty, twenty_twentyone]

            labels = ["7am", "8am", "9am", "10am", "11am", "12pm", "1pm",
                      "2pm", "3pm", "4pm", "5pm", "6pm", "7pm", "8pm", "9pm"]

            # get users in each teller and their total sales
            sales_that_day = Sales.objects.filter(created__contains=date)
            users_that_day = sales_that_day.values('user', 'user__email', 'total_net', 'created').annotate(
                c=Count('user__id', distinct=True))
            users = Sales.objects.values('user__email', 'user__name', 'terminal').annotate(Count('user')).annotate(
                Sum('total_net')).order_by().filter(created__contains=date)
            data = {
                "no_of_customers": no_of_customers,
                "date_total_sales": date_total_sales,
                "date": selected_sales_date,
                "prevdate": previous_sales_date,
                "default": default,
                "labels2": labels,
                "cashiers": users_that_day,
                "users": users,
                "sales_percent": sales_diff,
                "customer_percent": customer_diff,
                "prevdate_total_sales": prev_sales,
                "previous_sales": prevdate_total_sales,
            }
            if get_date:
                return TemplateResponse(request, 'dashboard/reports/sales/charts/by_date.html', data)
            else:
                return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_date.html', data)
        except ObjectDoesNotExist as e:
            if get_date:
                return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_date.html',
                                        {"error": e, "date": date})
            else:
                return TemplateResponse(request, 'dashboard/reports/sales/charts/by_date.html',
                                        {"error": e, "date": date})


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def get_sales_charts(request):
    label = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]
    default = [12, 19, 3, 5, 2, 3]
    total_sales = Sales.objects.all()
    today = datetime.date.today()
    todays_sales = Sales.objects.filter(created=today).annotate(Sum('total_net'))

    data = {
        "label": label,
        "default": default,
        "users": 10,
        "net": serializers.serialize('json', total_sales),
        "todays_sales": serializers.serialize('json', todays_sales),
    }
    return JsonResponse(data)


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def get_sales_by_week(request):
    date_from = request.GET.get('from')
    d_to = request.GET.get('to')
    date = d_to

    d = d_to.split('-')[-1]
    day_one = int(d) + 1

    m = d_to.split('-')[-2]
    y = d_to.split('-')[-3]

    lastday_of_month = monthrange(int(y), int(m))[1]
    '''
        ** - subtract number of days
    '''
    firstday_of_thisweek = datetime.datetime.strptime(date_from, '%Y-%m-%d')
    lastday_of_lastweek = firstday_of_thisweek - timedelta(days=(firstday_of_thisweek.weekday()) + 1)
    firstday_of_lastweek = lastday_of_lastweek - timedelta(days=7)
    # day differeces
    first_range_date = datetime.datetime.strptime(date_from, '%Y-%m-%d')
    second_range_date = datetime.datetime.strptime(d_to, '%Y-%m-%d')
    onedd = first_range_date + timedelta(days=1)
    '''
        s = Sales.objects.filter(created__year='2017', created__month='06', created__month__lte='08')
    '''
    date_range_diff = (second_range_date - first_range_date).days
    default3 = []
    labels3 = []
    if date_range_diff <= 8:
        for i in reversed(range(1, (date_range_diff) + 1, 1)):
            p = (second_range_date) - timedelta(days=i)
            amount = get_date_results(DateFormat(p).format('Y-m-d'))
            day = str(p.strftime("%A")[0:3]) + ' (' + str(DateFormat(p).format('jS F')) + ')'
            labels3.append(day)
            default3.append(amount)

    elif date_range_diff >= 9 and date_range_diff <= 20:
        for i in reversed(range(1, (date_range_diff) + 1, 2)):
            p = (second_range_date) - timedelta(days=i)
            amount = get_date_results(DateFormat(p).format('Y-m-d'))
            day = str(p.strftime("%A")[0:3]) + ' (*' + str(DateFormat(p).format('jS')) + ')'
            labels3.append(day)
            default3.append(amount)

    elif date_range_diff > 20 and date_range_diff <= 30:
        c = [first_range_date + timedelta(days=i) for i in range(0, (date_range_diff + 1), 4)]
        r = (second_range_date - c[-1]).days
        if r == 0:
            for i in range(0, (date_range_diff) + 1, 4):
                p = first_range_date + timedelta(days=i)
                p_next = p + timedelta(days=4)
                amount = get_date_results_range(DateFormat(p).format('Y-m-d'), DateFormat(p_next).format('Y-m-d'))
                r = str((DateFormat(p).format('d/m'))) + ' -0 ' + str(DateFormat(p_next).format('d/m'))
                labels3.append(r)
                default3.append(amount)
        else:
            last = c[-1]
            c.remove(last)
            for i in c:
                p_next = i + timedelta(days=3)
                amount = get_date_results_range(DateFormat(i).format('Y-m-d'), DateFormat(p_next).format('Y-m-d'))
                r = str((DateFormat(i).format('d/m'))) + ' -! ' + str(DateFormat(p_next).format('d/m'))
                labels3.append(r)
                default3.append(amount)

            if last == second_range_date:
                r = str((DateFormat(last).format('d/m'))) + ' -!! ' + str(DateFormat(second_range_date).format('d/m'))
                amount_that_date = get_date_results(DateFormat(last).format('Y-m-d'))
                default3.append(amount_that_date)
                labels3.append(r)
            else:
                r = str((DateFormat(last).format('d/m'))) + ' -!!! ' + str(DateFormat(second_range_date).format('d/m'))
                amount_that_date = get_date_results_range(DateFormat(last).format('Y-m-d'),
                                                          DateFormat(second_range_date).format('Y-m-d'))
                default3.append(amount_that_date)
                labels3.append(r)

    elif date_range_diff > 30 and date_range_diff <= 60:
        c = [first_range_date + timedelta(days=i) for i in range(0, (date_range_diff + 1), 8)]
        r = (second_range_date - c[-1]).days
        if r == 0:
            for i in range(0, (date_range_diff) + 1, 8):
                p = first_range_date + timedelta(days=i)
                p_next = p + timedelta(days=8)
                amount = get_date_results_range(DateFormat(p).format('Y-m-d'), DateFormat(p_next).format('Y-m-d'))
                r = str((DateFormat(p).format('d/m'))) + ' -* ' + str(DateFormat(p_next).format('d/m'))
                labels3.append(r)
                default3.append(amount)
        else:
            last = c[-1]
            c.remove(last)
            for i in c:
                p_next = i + timedelta(days=30)
                amount = get_date_results_range(DateFormat(i).format('Y-m-d'), DateFormat(p_next).format('Y-m-d'))
                r = str((DateFormat(i).format('d/m'))) + ' -* ' + str(DateFormat(p_next).format('d/m'))
                labels3.append(r)
                default3.append(amount)

            if last == second_range_date:
                r = str((DateFormat(last).format('d/m'))) + ' -** ' + str(DateFormat(second_range_date).format('d/m'))
                amount_that_date = get_date_results(DateFormat(last).format('Y-m-d'))
                default3.append(amount_that_date)
                labels3.append(r)
            else:
                r = str((DateFormat(last).format('d/m'))) + ' -*** ' + str(DateFormat(second_range_date).format('d/m'))
                amount_that_date = get_date_results_range(DateFormat(last).format('Y-m-d'),
                                                          DateFormat(second_range_date).format('Y-m-d'))
                default3.append(amount_that_date)
                labels3.append(r)

    elif date_range_diff > 60 and date_range_diff <= 350:
        for i in range(0, (date_range_diff) + 1, 30):
            p = (first_range_date) + timedelta(days=i)
            p_next = p + timedelta(days=30)
            amount = get_date_results_range(DateFormat(p).format('Y-m-d'), DateFormat(p_next).format('Y-m-d'))
            r = str((DateFormat(p).format('d'))) + '.' + str(p.strftime("%b")[0:3])
            labels3.append(r)
            default3.append(amount)

    elif 360 < date_range_diff <= 365:
        date_range_diff

    if len(str(int(d))) == 1:
        if len(str(int(d) + 1)) == 1:
            date_to = date.replace(d_to[-2:], str('0' + str(day_one)))
        else:
            date_to = date.replace(d_to[-2:], str(day_one))
    else:
        if int(d) == lastday_of_month:
            date_to = date.replace(d_to[-2:], str(d))
        else:
            date_to = date.replace(d_to[-2:], str(day_one))

    try:

        no_of_customers = Sales.objects.filter(created__range=[date_from, date_to]).count()

        items = SoldItem.objects.filter(sales__created__range=[date_from, date_to])

        # that date
        seven_eight = get_hours_results_range(date_from, date_to, 7, 8)
        eight_nine = get_hours_results_range(date_from, date_to, 8, 9)
        nine_ten = get_hours_results_range(date_from, date_to, 9, 10)
        ten_eleven = get_hours_results_range(date_from, date_to, 10, 11)
        eleven_twelve = get_hours_results_range(date_from, date_to, 11, 12)
        twelve_thirteen = get_hours_results_range(date_from, date_to, 12, 13)
        thriteen_fourteen = get_hours_results_range(date_from, date_to, 13, 14)
        fourteen_fifteen = get_hours_results_range(date_from, date_to, 14, 15)
        fifteen_sixteen = get_hours_results_range(date_from, date_to, 15, 16)
        sixteen_seventeen = get_hours_results_range(date_from, date_to, 16, 17)
        seventeen_eighteen = get_hours_results_range(date_from, date_to, 17, 18)
        eighteen_nineteen = get_hours_results_range(date_from, date_to, 18, 19)
        nineteen_twenty = get_hours_results_range(date_from, date_to, 19, 20)
        twenty_twentyone = get_hours_results_range(date_from, date_to, 20, 21)
        twentyone_twentytwo = get_hours_results_range(date_from, date_to, 21, 22)

        labels = ["7am", "8am", "9am", "10am", "11am", "12am", "1pm",
                  "2pm", "3pm", "4pm", "5pm", "6pm", "7pm", "8pm", "9pm"]

        default = [seven_eight, eight_nine, nine_ten, ten_eleven,
                   eleven_twelve, twelve_thirteen, thriteen_fourteen, fourteen_fifteen,
                   fifteen_sixteen, sixteen_seventeen, seventeen_eighteen,
                   eighteen_nineteen, nineteen_twenty, twenty_twentyone]

        labels2 = ["7am", "8am", "9am", "10am", "11am", "12pm", "1pm",
                   "2pm", "3pm", "4pm", "5pm", "6pm", "7pm", "8pm", "9pm"]

        # get users in each teller and their total sales
        sales_that_day = Sales.objects.filter(created__range=[date_from, date_to]).aggregate(Sum('total_net'))[
            'total_net__sum']
        users_that_day = Sales.objects.filter(created__range=[date_from, date_to]).values('user', 'user__email',
                                                                                          'total_net',
                                                                                          'created').annotate(
            c=Count('user__id', distinct=True))
        users = Sales.objects.values('user__email', 'user__name', 'terminal').annotate(Count('user')).annotate(
            Sum('total_net')).order_by().filter(created__range=[date_from, date_to])

        data = {
            "no_of_customers": no_of_customers,
            "date_total_sales": sales_that_day,
            "date_from": date_from,
            "date_to": date_to,
            "default": default,
            "labels2": labels2,
            "labels3": labels3,
            "default3": default3,
            "cashiers": users_that_day,
            "users": users
        }
        return TemplateResponse(request, 'dashboard/reports/sales/charts/by_date_range.html', data)
    except ObjectDoesNotExist as e:
        return TemplateResponse(request, 'dashboard/reports/sales/charts/by_date_range.html',
                                {"error": e, "date": date})


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def sales_user_chart(request):
    image = request.POST.get('img')
    today = datetime.datetime.now()
    get_date = request.GET.get('date')
    if get_date:
        date = get_date
    else:
        try:
            last_sale = Sales.objects.latest('id')
            date = DateFormat(last_sale.created).format('Y-m-d')
        except:
            date = DateFormat(datetime.datetime.today()).format('Y-m-d')

    if image:
        dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
        ImageData = image
        ImageData = dataUrlPattern.match(ImageData).group(2)

        users = Sales.objects.values('user__email', 'user__name', 'terminal').annotate(Count('user')).annotate(
            Sum('total_net')).order_by().filter(created__contains=date)
        sales_by_category_totals = users.aggregate(Sum('total_net__sum'))['total_net__sum__sum']
        new_sales = []
        for sales in users:
            color = "#%03x" % random.randint(0, 0xFFF)
            sales['color'] = color
            percent = (Decimal(sales['total_net__sum']) / Decimal(sales_by_category_totals)) * 100
            percentage = round(percent, 2)
            sales['percentage'] = percentage
            for s in range(0, users.count(), 1):
                sales['count'] = s
            new_sales.append(sales)

        data = {
            'today': last_sale.created,
            'sales_by_category': new_sales,
            'puller': request.user,
            'image': ImageData,
        }
        pdf = render_to_pdf('dashboard/reports/sales/charts/pdf/user_pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')

    if date:
        try:
            users = Sales.objects.values('user__email', 'user__name', 'terminal').annotate(Count('user')).annotate(
                Sum('total_net')).order_by().filter(created__contains=date)
            sales_by_category_totals = users.aggregate(Sum('total_net__sum'))['total_net__sum__sum']
            new_sales = []
            for sales in users:
                color = "#%03x" % random.randint(0, 0xFFF)
                sales['color'] = color
                percent = (Decimal(sales['total_net__sum']) / Decimal(sales_by_category_totals)) * 100
                percentage = round(percent, 2)
                sales['percentage'] = percentage
                for s in range(0, users.count(), 1):
                    sales['count'] = s
                new_sales.append(sales)
            categs = Sales.objects.values('user__id', 'user__email', 'user__name').annotate(
                Count('user', distinct=True)).order_by()
            this_year = today.year
            avg_m = Sales.objects.filter(created__year=this_year).annotate(c=Count('total_net'))
            highest_user_sales = new_sales[0]['user__name']
            default = []
            labels = []
            for i in range(1, (today.month + 1), 1):
                if len(str(i)) == 1:
                    m = str('0' + str(i))
                else:
                    m = str(i)
                try:
                    amount = get_user_results(highest_user_sales, str(today.year), m)
                except:
                    amount = 0
                labels.append(calendar.month_name[int(m)][0:3])
                default.append(amount)

            data = {
                "sales_by_category": new_sales,
                "categs": categs,
                "labels": labels,
                "default": default,
                "hcateg": highest_user_sales,
                "sales_date": date
            }
            # return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_user.html', data)
            return TemplateResponse(request, 'dashboard/reports/sales/ajax/user.html', data)
        except ObjectDoesNotExist:
            return TemplateResponse(request, 'dashboard/reports/sales/ajax/user.html', {"sales_date": date})
        except IndexError:
            return TemplateResponse(request, 'dashboard/reports/sales/ajax/user.html', {"sales_date": date})


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def get_user_sale_details(request):
    get_categ = request.GET.get('user')
    today = datetime.datetime.now()
    if get_categ:
        try:
            """ this year """
            this_year_sales = Sales.objects.filter(user__name__contains=get_categ, created__year=today.year
                                                   ).aggregate(Sum('total_net'))['total_net__sum']
            y_sales = Sales.objects.filter(created__year=today.year).aggregate(Sum('total_net'))['total_net__sum']
            try:
                ty_percent = round((Decimal(this_year_sales) / Decimal(y_sales)) * 100, 2)
                ty_others = 100 - ty_percent
            except:
                ty_percent = 0
                ty_others = 0

            """ this month """
            this_month_sales = Sales.objects.filter(user__name__contains=get_categ, created__year=today.year,
                                                    created__month=today.month).aggregate(Sum('total_net'))[
                'total_net__sum']
            m_sales = \
            Sales.objects.filter(created__year=today.year, created__month=today.month).aggregate(Sum('total_net'))[
                'total_net__sum']
            try:
                tm_percent = round((Decimal(this_month_sales) / Decimal(m_sales)) * 100, 2)
                tm_others = 100 - tm_percent
            except:
                tm_percent = 0
                tm_others = 0

            """ last year """
            last_year_sales = Sales.objects.filter(user__name__contains=get_categ, created__year=(today.year - 1)
                                                   ).aggregate(Sum('total_net'))['total_net__sum']
            ly_sales = Sales.objects.filter(created__year=(today.year - 1)).aggregate(Sum('total_net'))[
                'total_net__sum']
            try:
                ly_percent = round((Decimal(last_year_sales) / Decimal(ly_sales)) * 100, 2)
                ly_others = 100 - ly_percent
            except:
                ly_percent = 0
                ly_others = 0

            """ last month """
            last_month = today.month - 1 if today.month > 1 else 12
            last_month_sales = Sales.objects.filter(user__name__contains=get_categ, created__year=today.year,
                                                    created__month=last_month).aggregate(Sum('total_net'))[
                'total_net__sum']

            lm_sales = \
            Sales.objects.filter(created__year=today.year, created__month=last_month).aggregate(Sum('total_net'))[
                'total_net__sum']
            try:
                lm_percent = round((Decimal(last_month_sales) / Decimal(lm_sales)) * 100, 2)
                lm_others = 100 - lm_percent
            except:
                lm_percent = 0
                lm_others = 0
            last_sales = Sales.objects.filter(user__name__contains=get_categ).values('user__name', 'total_net',
                                                                                     'created').annotate(
                Sum('total_net', distinct=True)).order_by().latest('id')
            print get_categ

            data = {
                "category": get_categ,
                "this_year_sales": this_year_sales,
                "this_month_sales": this_month_sales,
                "last_year_sales": last_year_sales,
                "last_month_sales": last_month_sales,
                "ty_percent": ty_percent,
                "ty_others": ty_others,
                "tm_percent": tm_percent,
                "tm_others": tm_others,
                "ly_percent": ly_percent,
                "ly_others": ly_others,
                "lm_percent": lm_percent,
                "lm_others": lm_others,
                "last_sales": last_sales
            }
            return TemplateResponse(request, 'dashboard/reports/sales/charts/by_user.html', data)
        except ObjectDoesNotExist as e:
            return TemplateResponse(request, 'dashboard/reports/sales/charts/by_user.html', {})
        # return HttpResponse(e)


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def sales_terminal_chart(request):
    image = request.POST.get('img')
    today = datetime.datetime.now()
    get_date = request.GET.get('date')
    if get_date:
        date = get_date
    else:
        try:
            last_sale = Sales.objects.latest('id')
            date = DateFormat(last_sale.created).format('Y-m-d')
        except:
            date = DateFormat(datetime.datetime.today()).format('Y-m-d')

    if image:
        dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
        ImageData = image
        ImageData = dataUrlPattern.match(ImageData).group(2)

        terminals = Sales.objects.values('terminal__terminal_name', 'terminal').annotate(Count('terminal')).annotate(
            Sum('total_net')).order_by().filter(created__contains=date)
        sales_by_category_totals = terminals.aggregate(Sum('total_net__sum'))['total_net__sum__sum']
        new_sales = []
        for sales in terminals:
            color = "#%03x" % random.randint(0, 0xFFF)
            sales['color'] = color
            percent = (Decimal(sales['total_net__sum']) / Decimal(sales_by_category_totals)) * 100
            percentage = round(percent, 2)
            sales['percentage'] = percentage
            for s in range(0, terminals.count(), 1):
                sales['count'] = s
            new_sales.append(sales)

        data = {
            'today': last_sale.created,
            'sales_by_category': new_sales,
            'puller': request.user,
            'image': ImageData,
        }
        pdf = render_to_pdf('dashboard/reports/sales/charts/pdf/terminal_pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')

    if date:
        try:
            terminals = Sales.objects.values('terminal__terminal_name', 'terminal').annotate(
                Count('terminal')).annotate(
                Sum('total_net')).order_by().filter(created__contains=date)
            sales_by_category_totals = terminals.aggregate(Sum('total_net__sum'))['total_net__sum__sum']
            new_sales = []
            for sales in terminals:
                color = "#%03x" % random.randint(0, 0xFFF)
                sales['color'] = color
                percent = (Decimal(sales['total_net__sum']) / Decimal(sales_by_category_totals)) * 100
                percentage = round(percent, 2)
                sales['percentage'] = percentage
                for s in range(0, terminals.count(), 1):
                    sales['count'] = s
                new_sales.append(sales)
            categs = Terminal.objects.all()
            this_year = today.year
            avg_m = Sales.objects.filter(created__year=this_year).annotate(c=Count('total_net'))
            highest_user_sales = new_sales[0]['terminal__terminal_name']
            default = []
            labels = []
            for i in range(1, (today.month + 1), 1):
                if len(str(i)) == 1:
                    m = str('0' + str(i))
                else:
                    m = str(i)
                amount = get_terminal_results(highest_user_sales, str(today.year), m)
                labels.append(calendar.month_name[int(m)][0:3])
                default.append(amount)

            data = {
                "sales_by_category": new_sales,
                "categs": categs,
                "labels": labels,
                "default": default,
                "hcateg": highest_user_sales,
                "sales_date": date
            }
            # return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_teller.html', data)
            return TemplateResponse(request, 'dashboard/reports/sales/ajax/till.html', data)
        except ObjectDoesNotExist:
            return TemplateResponse(request, 'dashboard/reports/sales/ajax/till.html', {"sales_date": date})
        except IndexError:
            return TemplateResponse(request, 'dashboard/reports/sales/ajax/till.html', {"sales_date": date})


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def get_terminal_sale_details(request):
    get_categ = request.GET.get('terminal')
    today = datetime.datetime.now()
    if get_categ:
        try:
            """ this year """
            this_year_sales = Sales.objects.filter(terminal__terminal_name__contains=get_categ, created__year=today.year
                                                   ).aggregate(Sum('total_net'))['total_net__sum']
            y_sales = Sales.objects.filter(created__year=today.year).aggregate(Sum('total_net'))['total_net__sum']
            try:
                ty_percent = round((Decimal(this_year_sales) / Decimal(y_sales)) * 100, 2)
                ty_others = 100 - ty_percent
            except:
                ty_percent = 0
                ty_others = 0

            """ this month """
            this_month_sales = \
            Sales.objects.filter(terminal__terminal_name__contains=get_categ, created__year=today.year,
                                 created__month=today.month).aggregate(Sum('total_net'))['total_net__sum']
            m_sales = \
            Sales.objects.filter(created__year=today.year, created__month=today.month).aggregate(Sum('total_net'))[
                'total_net__sum']
            try:
                tm_percent = round((Decimal(this_month_sales) / Decimal(m_sales)) * 100, 2)
                tm_others = 100 - tm_percent
            except:
                tm_percent = 0
                tm_others = 0

            """ last year """
            last_year_sales = \
            Sales.objects.filter(terminal__terminal_name__contains=get_categ, created__year=(today.year - 1)
                                 ).aggregate(Sum('total_net'))['total_net__sum']
            ly_sales = Sales.objects.filter(created__year=(today.year - 1)).aggregate(Sum('total_net'))[
                'total_net__sum']
            try:
                ly_percent = round((Decimal(last_year_sales) / Decimal(ly_sales)) * 100, 2)
                ly_others = 100 - ly_percent
            except:
                ly_percent = 0
                ly_others = 0

            """ last month """
            last_month = today.month - 1 if today.month > 1 else 12
            last_month_sales = \
            Sales.objects.filter(terminal__terminal_name__contains=get_categ, created__year=today.year,
                                 created__month=last_month).aggregate(Sum('total_net'))['total_net__sum']

            lm_sales = \
            Sales.objects.filter(created__year=today.year, created__month=last_month).aggregate(Sum('total_net'))[
                'total_net__sum']
            try:
                lm_percent = round((Decimal(last_month_sales) / Decimal(lm_sales)) * 100, 2)
                lm_others = 100 - lm_percent
            except:
                lm_percent = 0
                lm_others = 0
            last_sales = Sales.objects.filter(terminal__terminal_name__contains=get_categ).values(
                'terminal__terminal_name', 'total_net', 'created').annotate(
                Sum('total_net', distinct=True)).order_by().latest('id')
            print get_categ

            data = {
                "category": get_categ,
                "this_year_sales": this_year_sales,
                "this_month_sales": this_month_sales,
                "last_year_sales": last_year_sales,
                "last_month_sales": last_month_sales,
                "ty_percent": ty_percent,
                "ty_others": ty_others,
                "tm_percent": tm_percent,
                "tm_others": tm_others,
                "ly_percent": ly_percent,
                "ly_others": ly_others,
                "lm_percent": lm_percent,
                "lm_others": lm_others,
                "last_sales": last_sales
            }
            return TemplateResponse(request, 'dashboard/reports/sales/charts/by_terminal.html', data)
        except ObjectDoesNotExist as e:
            return TemplateResponse(request, 'dashboard/reports/sales/charts/by_terminal.html', {})


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def sales_product_chart(request):
    get_date = request.GET.get('date')
    image = request.POST.get('img')
    today = datetime.datetime.now()
    if get_date:
        date = get_date
    else:
        try:
            last_sale = Sales.objects.latest('id')
            date = DateFormat(last_sale.created).format('Y-m-d')
        except:
            date = DateFormat(datetime.datetime.today()).format('Y-m-d')

    if image:
        dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
        ImageData = image
        ImageData = dataUrlPattern.match(ImageData).group(2)

        sales_by_category = SoldItem.objects.filter(sales__created__contains=date).values('product_category').annotate(
            c=Count('product_category', distinct=True)).annotate(Sum('total_cost')).order_by('-total_cost__sum')[:5]
        sales_by_category_totals = sales_by_category.aggregate(Sum('total_cost__sum'))['total_cost__sum__sum']
        new_sales = []
        for sales in sales_by_category:
            color = "#%03x" % random.randint(0, 0xFFF)
            sales['color'] = color
            percent = (Decimal(sales['total_cost__sum']) / Decimal(sales_by_category_totals)) * 100
            percentage = round(percent, 2)
            sales['percentage'] = percentage
            for s in range(0, sales_by_category.count(), 1):
                sales['count'] = s
            new_sales.append(sales)

        data = {
            'today': last_sale.created,
            'sales_by_category': new_sales,
            'puller': request.user,
            'image': ImageData,
        }
        pdf = render_to_pdf('dashboard/reports/sales/charts/pdf/product_pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    if date:
        try:
            sales_by_category = SoldItem.objects.filter(sales__created__contains=date).values('product_name').annotate(
                c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).order_by('-total_cost__sum')[:5]
            sales_by_category_totals = sales_by_category.aggregate(Sum('total_cost__sum'))['total_cost__sum__sum']
            new_sales = []
            for sales in sales_by_category:
                color = "#%03x" % random.randint(0, 0xFFF)
                sales['color'] = color
                percent = (Decimal(sales['total_cost__sum']) / Decimal(sales_by_category_totals)) * 100
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
                "sales_by_category": new_sales,
                "categs": categs,
                "avg": avg_m,
                "labels": labels,
                "default": default,
                "hcateg": highest_category_sales,
                "sales_date": date
            }
            # return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_product.html', data)
            return TemplateResponse(request, 'dashboard/reports/sales/ajax/items.html', data)
        except ObjectDoesNotExist as e:
            return TemplateResponse(request, 'dashboard/reports/sales/ajax/items.html', {'sales_date': date})
        except IndexError as e:
            return TemplateResponse(request, 'dashboard/reports/sales/ajax/items.html', {'sales_date': date})


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def get_product_sale_details(request):
    get_categ = request.GET.get('item')
    today = datetime.datetime.now()
    if get_categ:
        try:
            """ this year """
            this_year_sales = SoldItem.objects.filter(product_name__contains=get_categ, sales__created__year=today.year
                                                      ).aggregate(Sum('total_cost'))['total_cost__sum']
            y_sales = SoldItem.objects.filter(sales__created__year=today.year).aggregate(Sum('total_cost'))[
                'total_cost__sum']
            try:
                ty_percent = round((Decimal(this_year_sales) / Decimal(y_sales)) * 100, 2)
                ty_others = 100 - ty_percent
            except:
                ty_percent = 0
                ty_others = 0

            """ this month """
            this_month_sales = \
            SoldItem.objects.filter(product_name__contains=get_categ, sales__created__year=today.year,
                                    sales__created__month=today.month).aggregate(Sum('total_cost'))['total_cost__sum']
            m_sales = \
            SoldItem.objects.filter(sales__created__year=today.year, sales__created__month=today.month).aggregate(
                Sum('total_cost'))['total_cost__sum']
            try:
                tm_percent = round((Decimal(this_month_sales) / Decimal(m_sales)) * 100, 2)
                tm_others = 100 - tm_percent
            except:
                tm_percent = 0
                tm_others = 0

            """ last year """
            last_year_sales = \
            SoldItem.objects.filter(product_name__contains=get_categ, sales__created__year=(today.year - 1)
                                    ).aggregate(Sum('total_cost'))['total_cost__sum']
            ly_sales = SoldItem.objects.filter(sales__created__year=(today.year - 1)).aggregate(Sum('total_cost'))[
                'total_cost__sum']
            try:
                ly_percent = round((Decimal(last_year_sales) / Decimal(ly_sales)) * 100, 2)
                ly_others = 100 - ly_percent
            except:
                ly_percent = 0
                ly_others = 0

            """ last month """
            last_month = today.month - 1 if today.month > 1 else 12
            last_month_sales = \
            SoldItem.objects.filter(product_name__contains=get_categ, sales__created__year=today.year,
                                    sales__created__month=last_month).aggregate(Sum('total_cost'))['total_cost__sum']

            lm_sales = \
            SoldItem.objects.filter(sales__created__year=today.year, sales__created__month=last_month).aggregate(
                Sum('total_cost'))['total_cost__sum']
            try:
                lm_percent = round((Decimal(last_month_sales) / Decimal(lm_sales)) * 100, 2)
                lm_others = 100 - lm_percent
            except:
                lm_percent = 0
                lm_others = 0
            last_sales = SoldItem.objects.filter(product_name__contains=get_categ).values('product_name', 'total_cost',
                                                                                          'sales__created').annotate(
                Sum('total_cost', distinct=True)).order_by().latest('sales__id')

            data = {
                "category": get_categ,
                "this_year_sales": this_year_sales,
                "this_month_sales": this_month_sales,
                "last_year_sales": last_year_sales,
                "last_month_sales": last_month_sales,
                "ty_percent": ty_percent,
                "ty_others": ty_others,
                "tm_percent": tm_percent,
                "tm_others": tm_others,
                "ly_percent": ly_percent,
                "ly_others": ly_others,
                "lm_percent": lm_percent,
                "lm_others": lm_others,
                "last_sales": last_sales
            }
            return TemplateResponse(request, 'dashboard/reports/sales/charts/by_product.html', data)
        except ObjectDoesNotExist as e:
            return TemplateResponse(request, 'dashboard/reports/sales/charts/by_product.html', {})
