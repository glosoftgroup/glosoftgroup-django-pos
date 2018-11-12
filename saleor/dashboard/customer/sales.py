from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.db.models import Count, Sum, Q
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.http import HttpResponse
from django.utils.dateformat import DateFormat
import datetime

# from datetime import date
from ...utils import render_to_pdf, default_logo
from ..views import staff_member_required
from ...customer.models import Customer
from ...sale.models import Sales, SoldItem

from structlog import get_logger

logger = get_logger(__name__)


@staff_member_required
def sales_paginate(request):
    page = int(request.GET.get('page'))
    pk = int(request.GET.get('cpk'))
    list_sz = request.GET.get('size')
    date = request.GET.get('date')
    action = request.GET.get('action')
    p2_sz = request.GET.get('psize')
    gid = request.GET.get('gid')
    today_formart = DateFormat(datetime.date.today())
    today = today_formart.format('Y-m-d')
    ts = Sales.objects.filter(created__icontains=today)
    tsum = ts.aggregate(Sum('total_net'))
    total_sales = Sales.objects.aggregate(Sum('total_net'))
    total_tax = Sales.objects.aggregate(Sum('total_tax'))

    customer = get_object_or_404(Customer, pk=pk)
    csales = Sales.objects.filter(customer=customer)

    if request.GET.get('sth'):

        all_sales = csales.filter(created__icontains=date).order_by('-id')
        sales = []
        for sale in all_sales:
            quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
            setattr(sale, 'quantity', quantity['c'])
            sales.append(sale)
        if date:
            try:
                all_salesd = csales.filter(created__icontains=date).order_by('-id')
                that_date_sum = csales.filter(created__contains=date).aggregate(Sum('total_net'))
                sales = []
                for sale in all_salesd:
                    quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                    setattr(sale, 'quantity', quantity['c'])
                    sales.append(sale)

                if p2_sz and gid:
                    paginator = Paginator(sales, int(p2_sz))
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/customer/sales/paginate.html',
                                            {'sales': sales, 'gid': date})

                paginator = Paginator(sales, 10)
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/customer/sales/p2.html',
                                        {'sales': sales, 'pn': paginator.num_pages, 'sz': 10, 'gid': date,
                                         'total_sales': total_sales, 'total_tax': total_tax, 'tsum': tsum,
                                         'that_date_sum': that_date_sum, 'date': date, 'today': today,
                                         'customer': customer})

            except ObjectDoesNotExist as e:
                return TemplateResponse(request, 'dashboard/customer/sales/p2.html',
                                        {'date': date, 'customer': customer})
        if action:
            try:
                all_sales2 = csales.filter(created__icontains=date).order_by('-id')
                sales = []
                for sale in all_sales2:
                    quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                    setattr(sale, 'quantity', quantity['c'])
                    sales.append(sale)
                if p2_sz and gid:
                    paginator = Paginator(sales, int(p2_sz))
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/customer/sales/paginate.html',
                                            {'sales': sales, 'gid': action, 'customer': customer})

                paginator = Paginator(sales, 10)
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/customer/sales/p2.html',
                                        {'sales': sales, 'pn': paginator.num_pages, 'sz': 10, 'gid': action,
                                         'total_sales': total_sales, 'total_tax': total_tax, 'tsum': tsum,
                                         'customer': customer})

            except ObjectDoesNotExist as e:
                return TemplateResponse(request, 'dashboard/customer/sales/p2.html',
                                        {'date': date, 'customer': customer})
    else:
        try:
            last_sale = Sales.objects.latest('id')
            all_sales = csales
            sales = []
            for sale in all_sales:
                quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                setattr(sale, 'quantity', quantity['c'])
                sales.append(sale)

            if gid:
                date = gid
                try:
                    all_sales2 = csales.filter(created__icontains=date).order_by('-id')
                    that_date = csales.filter(created__icontains=date)
                    that_date_sum = that_date.aggregate(Sum('total_net'))
                    sales = []
                    for sale in all_sales2:
                        quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                        setattr(sale, 'quantity', quantity['c'])
                        sales.append(sale)
                    if p2_sz:
                        paginator = Paginator(sales, int(p2_sz))
                        sales = paginator.page(page)
                        return TemplateResponse(request, 'dashboard/customer/sales/paginate.html',
                                                {'sales': sales, 'gid': date, 'customer': customer})

                    paginator = Paginator(sales, 10)
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/customer/sales/p2.html',
                                            {'sales': sales, 'pn': paginator.num_pages, 'sz': 10, 'gid': date,
                                             'total_sales': total_sales, 'total_tax': total_tax, 'tsum': tsum,
                                             'that_date_sum': that_date_sum, 'date': date, 'today': today,
                                             'customer': customer})

                except ObjectDoesNotExist as e:
                    return TemplateResponse(request, 'dashboard/customer/sales/p2.html',
                                            {'date': date, 'customer': customer})

            if list_sz:
                paginator = Paginator(sales, int(list_sz))
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/customer/sales/p2.html',
                                        {'sales': sales, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0,
                                         'total_sales': total_sales, 'total_tax': total_tax, 'tsum': tsum,
                                         'customer': customer})
            else:
                paginator = Paginator(sales, 10)
            if p2_sz:
                paginator = Paginator(sales, int(p2_sz))
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/customer/sales/paginate.html',
                                        {'sales': sales, 'customer': customer})

            try:
                sales = paginator.page(page)
            except PageNotAnInteger:
                sales = paginator.page(1)
            except InvalidPage:
                sales = paginator.page(1)
            except EmptyPage:
                sales = paginator.page(paginator.num_pages)
            return TemplateResponse(request, 'dashboard/customer/sales/paginate.html',
                                    {'sales': sales, 'customer': customer})
        except ObjectDoesNotExist as e:
            return TemplateResponse(request, 'dashboard/customer/sales/p2.html', {'date': date, 'customer': customer})


@staff_member_required
def sales_search(request):
    if request.is_ajax():
        pk = int(request.GET.get('cpk'))
        page = int(request.GET.get('page', 1))
        list_sz = request.GET.get('size')
        p2_sz = request.GET.get('psize')
        q = request.GET.get('q')
        if list_sz is None:
            sz = 10
        else:
            sz = list_sz

        if q is not None:
            customer = get_object_or_404(Customer, pk=pk)
            csales = Sales.objects.filter(customer=customer)
            all_sales = csales.filter(
                Q(invoice_number__icontains=q) |
                Q(terminal__terminal_name__icontains=q) |
                Q(created__icontains=q) |
                Q(user__email__icontains=q) |
                Q(customer__name__icontains=q) |
                Q(user__name__icontains=q)).order_by('id')
            sales = []

            if request.GET.get('gid'):
                csales = all_sales.filter(created__icontains=request.GET.get('gid'))
                for sale in csales:
                    quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                    setattr(sale, 'quantity', quantity['c'])
                    sales.append(sale)

                if p2_sz:
                    paginator = Paginator(sales, int(p2_sz))
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/customer/sales/paginate.html',
                                            {'customer': customer, 'sales': sales})

                if list_sz:
                    paginator = Paginator(sales, int(list_sz))
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/customer/sales/search.html',
                                            {'customer': customer, 'sales': sales, 'pn': paginator.num_pages,
                                             'sz': list_sz,
                                             'gid': request.GET.get('gid'), 'q': q})

                paginator = Paginator(sales, 10)
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/customer/sales/search.html',
                                        {'customer': customer, 'sales': sales, 'pn': paginator.num_pages, 'sz': sz,
                                         'gid': request.GET.get('gid')})

            else:
                for sale in all_sales:
                    quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                    setattr(sale, 'quantity', quantity['c'])
                    sales.append(sale)

                if list_sz:
                    print ('lst')
                    paginator = Paginator(sales, int(list_sz))
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/customer/sales/search.html',
                                            {'customer': customer, 'sales': sales, 'pn': paginator.num_pages,
                                             'sz': list_sz, 'gid': 0,
                                             'q': q})

                if p2_sz:
                    print ('pst')
                    paginator = Paginator(sales, int(p2_sz))
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/customer/sales/paginate.html',
                                            {'customer': customer, 'sales': sales})

                paginator = Paginator(sales, 10)
                try:
                    sales = paginator.page(page)
                except PageNotAnInteger:
                    sales = paginator.page(1)
                except InvalidPage:
                    sales = paginator.page(1)
                except EmptyPage:
                    sales = paginator.page(paginator.num_pages)
                if p2_sz:
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/customer/sales/paginate.html',
                                            {'customer': customer, 'sales': sales})

                return TemplateResponse(request, 'dashboard/customer/sales/search.html',
                                        {'customer': customer, 'sales': sales, 'pn': paginator.num_pages, 'sz': sz,
                                         'q': q})


@staff_member_required
def sales_list_pdf(request):
    if request.is_ajax():
        q = request.GET.get('q')
        gid = request.GET.get('gid')
        pk = int(request.GET.get('cpk'))

        if gid:
            gid = gid
        else:
            gid = None

        sales = []

        customer = get_object_or_404(Customer, pk=pk)
        csales = Sales.objects.filter(customer=customer)
        if q is not None:
            all_sales = csales.filter(
                Q(invoice_number__icontains=q) |
                Q(terminal__terminal_name__icontains=q) |
                Q(created__icontains=q) |
                Q(user__email__icontains=q) |
                Q(customer__name__icontains=q) |
                Q(user__name__icontains=q)).order_by('id')
            sales = []

            if gid:
                csales = all_sales.filter(created__icontains=gid)
                for sale in csales:
                    quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                    setattr(sale, 'quantity', quantity['c'])
                    sales.append(sale)
            else:
                for sale in all_sales:
                    quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                    setattr(sale, 'quantity', quantity['c'])
                    sales.append(sale)

        elif gid:
            csales = csales.filter(created__icontains=gid)
            for sale in csales:
                quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                setattr(sale, 'quantity', quantity['c'])
                sales.append(sale)
        else:
            for sale in csales:
                quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                setattr(sale, 'quantity', quantity['c'])
                sales.append(sale)

        img = default_logo()
        data = {
            'today': datetime.date.today(),
            'sales': sales,
            'puller': request.user,
            'image': img,
            'gid': gid,
            'customer': customer
        }
        pdf = render_to_pdf('dashboard/customer/sales/pdf/saleslist.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


@staff_member_required
def sales_detail(request, pk=None):
    try:
        sale = Sales.objects.get(pk=pk)
        items = SoldItem.objects.filter(sales=sale)
        img = default_logo()
        data = {
            'today': datetime.date.today(),
            'items': items,
            'sale': sale,
            'puller': request.user,
            'image': img
        }
        pdf = render_to_pdf('dashboard/customer/sales/pdf/pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    except ObjectDoesNotExist as e:
        logger.error(e)
