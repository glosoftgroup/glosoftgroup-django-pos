
from django.http import HttpResponse
from django.db.models import Sum
from django.template.defaultfilters import date
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
import datetime
from datetime import date, timedelta
from django.utils.dateformat import DateFormat
import logging
import random
import csv
from django.utils.encoding import smart_str
import dateutil.relativedelta

import re
from ..views import staff_member_required
from ...userprofile.models import User
from ...credit.models import Credit, CreditedItem
from ...decorators import permission_decorator
from ...utils import render_to_pdf, image64

from structlog import get_logger

logger = get_logger(__name__)


@staff_member_required
def chart_pdf(request, image):
    dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
    ImageData = image
    ImageData = dataUrlPattern.match(ImageData).group(2)

    users = User.objects.all()
    data = {
        'today': date.today(),
        'users': users,
        'puller': request.user,
        'image': ImageData
    }
    pdf = render_to_pdf('dashboard/reports/credit/charts/pdf/pdf.html', data)
    return HttpResponse(pdf, content_type='application/pdf')


@staff_member_required
def sales_export_csv(request, image):
    dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
    ImageData = image
    ImageData = dataUrlPattern.match(ImageData).group(2)
    fh = open("imageToSave.png", "wb")
    fh.write(ImageData.decode('base64'))
    fh.close()

    pdfname = 'users' + str(random.random())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + pdfname + '.csv"'
    qs = User.objects.all()
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(u"ID"),
        smart_str(u"Name"),
        smart_str(u"Email"),
        smart_str(u"Image"),
    ])
    for obj in qs:
        writer.writerow([
            smart_str(obj.pk),
            smart_str(obj.name),
            smart_str(obj.email),
            smart_str(fh),
        ])
    return response


@staff_member_required
def sales_list_pdf(request):
    if request.is_ajax():
        q = request.GET.get('q')
        gid = request.GET.get('gid')

        if gid:
            date = gid
        else:
            date = None

        month = request.GET.get('month')
        year = request.GET.get('year')
        period = request.GET.get('period')

        if year and month:
            if len(str(month)) == 1:
                m = '0' + str(month)
                fdate = str(year) + '-' + m
            else:
                fdate = str(year) + '-' + str(month)

            d = datetime.datetime.strptime(fdate, "%Y-%m")
        elif year:
            fdate = str(year)
            d = datetime.datetime.strptime(fdate, "%Y")

        if period == 'year':
            lastyear = d - dateutil.relativedelta.relativedelta(years=1)
            y = str(lastyear.strftime("%Y"))
            credits = Credit.objects.filter(created__year__range=[y, year])
            date_period = str(lastyear.strftime("%Y")) + ' - ' + str(
                datetime.datetime.now().strftime("%m")) + '/' + str(year)
        elif period == 'month':
            credits = Credit.objects.filter(created__year=str(d.strftime("%Y")), created__month=str(d.strftime("%m")))
            date_period = str(datetime.datetime.strptime(month, "%m").strftime("%B")) + '/' + str(
                datetime.datetime.strptime(year, "%Y").strftime("%Y"))
        elif period == 'quarter':
            p = d - dateutil.relativedelta.relativedelta(months=3)
            month = str(datetime.datetime.strptime(month, "%m").strftime("%m"))
            credits = Credit.objects.filter(created__year=str(p.strftime("%Y")),
                                            created__month__range=[str(p.strftime("%m")), month])
            date_period = str(p.strftime("%B")) + '/' + str(p.strftime("%Y")) + ' - ' + str(
                datetime.datetime.strptime(month, "%m").strftime("%B")) + '/' + str(year)
        else:
            credits = Credit.objects.all()
            if not date:
                date = DateFormat(datetime.datetime.today()).format('Y-m-d')
            date_period = date

        sales = []
        if q is not None:
            all_sales = credits.filter(
                Q(invoice_number__icontains=q) |
                Q(terminal__terminal_name__icontains=q) |
                Q(created__icontains=q) |
                Q(customer__name__icontains=q) | Q(customer__mobile__icontains=q) |
                Q(credititems__product_name__icontains=q) |
                Q(user__email__icontains=q) |
                Q(user__name__icontains=q)).order_by('id').distinct()

            if date:
                csales = all_sales.filter(created__icontains=date)
                for sale in csales:
                    quantity = CreditedItem.objects.filter(credit=sale).aggregate(c=Sum('quantity'))
                    setattr(sale, 'quantity', quantity['c'])
                    sales.append(sale)
            else:
                for sale in all_sales:
                    quantity = CreditedItem.objects.filter(credit=sale).aggregate(c=Sum('quantity'))
                    setattr(sale, 'quantity', quantity['c'])
                    sales.append(sale)
            total_sales_amount = all_sales.filter(created__icontains=date).aggregate(Sum('total_net'))

        elif date:
            csales = credits.filter(created__icontains=date)
            for sale in csales:
                quantity = CreditedItem.objects.filter(credit=sale).aggregate(c=Sum('quantity'))
                setattr(sale, 'quantity', quantity['c'])
                sales.append(sale)
            total_sales_amount = csales.aggregate(Sum('total_net'))
        else:
            try:
                last_sale = Credit.objects.latest('id')
                gid = DateFormat(last_sale.created).format('Y-m-d')
            except:
                gid = DateFormat(datetime.datetime.today()).format('Y-m-d')

            csales = credits.filter(created__icontains=date)
            for sale in csales:
                quantity = CreditedItem.objects.filter(credit=sale).aggregate(c=Sum('quantity'))
                setattr(sale, 'quantity', quantity['c'])
                sales.append(sale)
            total_sales_amount = csales.aggregate(Sum('total_net'))

        img = image64()
        data = {
            'today': datetime.datetime.today(),
            'sales': sales,
            'puller': request.user,
            'image': img,
            'gid': date,
            'date_period': date_period,
            "total_sales_amount": total_sales_amount
        }
        pdf = render_to_pdf('dashboard/reports/credit/pdf/saleslist_pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def sales_detail(request, pk=None):
    try:
        sale = Credit.objects.get(pk=pk)
        items = CreditedItem.objects.filter(credit=sale)
        img = image64()
        data = {
            'today': date.today(),
            'items': items,
            'sale': sale,
            'puller': request.user,
            'image': img
        }
        pdf = render_to_pdf('dashboard/reports/credit/pdf/pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    except ObjectDoesNotExist as e:
        logger.error(e)


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def sales_category(request):
    try:
        image = request.GET.get('image')
        sales_date = request.GET.get('date')
        if not sales_date:
            sales_date = None

        img = image64()
        data = {
            'today': date.today(),
            'puller': request.user,
            'image': img,
            'category': image,
            'sales_date': sales_date
        }
        print (sales_date)
        pdf = render_to_pdf('dashboard/reports/credit/pdf/category.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    except ObjectDoesNotExist as e:
        logger.error(e)


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def sales_items(request):
    try:
        image = request.GET.get('image')
        sales_date = request.GET.get('date')
        if not sales_date:
            sales_date = None

        img = image64()
        data = {
            'today': date.today(),
            'puller': request.user,
            'image': img,
            'category': image,
            'sales_date': sales_date
        }
        print (sales_date)
        pdf = render_to_pdf('dashboard/reports/credit/pdf/items.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    except ObjectDoesNotExist as e:
        logger.error(e)


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def sales_user(request):
    try:
        image = request.GET.get('image')
        sales_date = request.GET.get('date')
        if not sales_date:
            sales_date = None

        img = image64()
        data = {
            'today': date.today(),
            'puller': request.user,
            'image': img,
            'category': image,
            'sales_date': sales_date
        }
        print (sales_date)
        pdf = render_to_pdf('dashboard/reports/credit/pdf/user.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    except ObjectDoesNotExist as e:
        logger.error(e)


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def sales_tills(request):
    try:
        image = request.GET.get('image')
        sales_date = request.GET.get('date')
        if not sales_date:
            sales_date = None

        img = image64()
        data = {
            'today': date.today(),
            'puller': request.user,
            'image': img,
            'category': image,
            'sales_date': sales_date
        }
        print (sales_date)
        pdf = render_to_pdf('dashboard/reports/credit/pdf/till.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    except ObjectDoesNotExist as e:
        logger.error(e)
