from django.core.exceptions import ObjectDoesNotExist
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.db.models import Q
from django.template.defaultfilters import date
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from datetime import date
import logging

from ..views import staff_member_required
from ...purchase.models import PurchaseProduct

from ...decorators import permission_decorator, user_trail
from ...utils import render_to_pdf
import csv
import random
from django.utils.encoding import smart_str

from structlog import get_logger

logger = get_logger(__name__)


@staff_member_required
@permission_decorator('reports.view_purchase_reports')
def purchase_reports(request):
    try:
        queryset_list = PurchaseProduct.objects.all().order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(queryset_list, 10)
        try:
            queryset_list = paginator.page(page)
        except PageNotAnInteger:
            queryset_list = paginator.page(1)
        except InvalidPage:
            queryset_list = paginator.page(1)
        except EmptyPage:
            queryset_list = paginator.page(paginator.num_pages)
        purchases = queryset_list
        user_trail(request.user.name, 'accessed the purchase reports page', 'view')
        logger.info('User: ' + str(request.user.name) + ' accessed the purchase reports page page')

        all_purchases = 0
        for purchase in queryset_list:
            all_purchases += purchase.get_total_cost()
        data = {
            "purchases": purchases,
            "all_purchases": all_purchases,
            'totalp': paginator.num_pages,
        }
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/reports/purchase/purchases.html', data)
    except TypeError as e:
        logger.error(e)
        return HttpResponse('error accessing purchase reports')


@staff_member_required
def purchase_paginate(request):
    page = int(request.GET.get('page'))
    list_sz = request.GET.get('size')
    date = request.GET.get('date')
    action = request.GET.get('action')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    gid = request.GET.get('gid')

    if date:
        try:
            date_purchases = PurchaseProduct.objects.filter(created__icontains=date).order_by('-id')
            all_purchases = 0
            for purchase in date_purchases:
                all_purchases += purchase.get_total_cost()

            if p2_sz and gid:
                paginator = Paginator(date_purchases, int(p2_sz))
                purchases = paginator.page(page)
                data = {
                    "purchases": purchases,
                    "all_purchases": all_purchases,
                    "gid": date,
                }

                return TemplateResponse(request, 'dashboard/reports/purchase/paginate.html',
                                        data)

            paginator = Paginator(date_purchases, 10)
            purchases = paginator.page(page)
            data = {
                "purchases": purchases,
                "all_purchases": all_purchases,
                "gid": date, 'pn': paginator.num_pages, 'sz': 10, 'gid': date,
                'date': date
            }

            return TemplateResponse(request, 'dashboard/reports/purchase/p2.html', data)

        except ObjectDoesNotExist as e:
            return TemplateResponse(request, 'dashboard/reports/purchase/p2.html', {'date': date})
    try:
        purchases = PurchaseProduct.objects.all().order_by('id')
        total_purchases = 0
        for purchase in purchases:
            total_purchases += purchase.get_total_cost()

        if list_sz:
            paginator = Paginator(purchases, int(list_sz))
            purchases = paginator.page(page)
            ctx = {
                'all_purchases': total_purchases,
                'purchases': purchases,
                'pn': paginator.num_pages,
                'sz': list_sz, 'gid': 0
            }
            return TemplateResponse(request, 'dashboard/reports/purchase/p2.html', ctx)
        else:
            paginator = Paginator(purchases, 10)
        if p2_sz:
            paginator = Paginator(purchases, int(p2_sz))
            purchases = paginator.page(page)
            return TemplateResponse(request, 'dashboard/reports/purchase/paginate.html', {'purchases': purchases})

        try:
            purchases = paginator.page(page)
        except PageNotAnInteger:
            purchases = paginator.page(1)
        except InvalidPage:
            purchases = paginator.page(1)
        except EmptyPage:
            purchases = paginator.page(paginator.num_pages)
            data = {
                "purchases": purchases,
                "all_purchases": total_purchases,
                "gid": date, 'pn': paginator.num_pages, 'sz': 10,
                'date': date
            }

        return TemplateResponse(request, 'dashboard/reports/purchase/paginate.html', data)
    except Exception, e:
        logger.error(e)


@staff_member_required
def purchase_search(request):
    if request.is_ajax():
        page = request.GET.get('page', 1)
        list_sz = request.GET.get('size', 10)
        p2_sz = request.GET.get('psize')
        q = request.GET.get('q')
        if list_sz is None:
            sz = 10
        else:
            sz = list_sz

        if q is not None:
            purchases = PurchaseProduct.objects.filter(
                Q(invoice_number__icontains=q) |
                Q(stock__variant__product__name__icontains=q) |
                Q(created__icontains=q) |
                Q(supplier__name__icontains=q)).order_by('id')
            all_purchases = 0
            for purchase in purchases:
                all_purchases += purchase.get_total_cost()

            if request.GET.get('gid'):
                purchases = purchases.filter(created__icontains=request.GET.get('gid'))

                if p2_sz:
                    paginator = Paginator(purchases, int(p2_sz))
                    purchases = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/reports/purchase/paginate.html',
                                            {'purchases': purchases})

                if list_sz:
                    paginator = Paginator(purchases, int(list_sz))
                    purchases = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/reports/purchase/search.html',
                                            {'purchases': purchases, "all_purchases": all_purchases,
                                             'pn': paginator.num_pages, 'sz': list_sz,
                                             'gid': request.GET.get('gid'), 'q': q})

                paginator = Paginator(purchases, 10)
                purchases = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/purchase/search.html',
                                        {'purchases': purchases, "all_purchases": all_purchases,
                                         'pn': paginator.num_pages, 'sz': sz,
                                         'gid': request.GET.get('gid')})

            else:

                if list_sz:
                    paginator = Paginator(purchases, int(list_sz))
                    purchases = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/reports/purchase/search.html',
                                            {'purchases': purchases, "all_purchases": all_purchases,
                                             'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0,
                                             'q': q})

                if p2_sz:
                    paginator = Paginator(purchases, int(p2_sz))
                    purchases = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/reports/purchase/paginate.html',
                                            {'purchases': purchases})

                paginator = Paginator(purchases, 10)
                try:
                    purchases = paginator.page(page)
                except PageNotAnInteger:
                    purchases = paginator.page(1)
                except InvalidPage:
                    purchases = paginator.page(1)
                except EmptyPage:
                    purchases = paginator.page(paginator.num_pages)
                if p2_sz:
                    purchases = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/reports/purchase/paginate.html',
                                            {'purchases': purchases})

                return TemplateResponse(request, 'dashboard/reports/purchase/search.html',
                                        {'purchases': purchases, "all_purchases": all_purchases,
                                         'pn': paginator.num_pages, 'sz': sz, 'q': q})


@staff_member_required
def purchase_pdf(request):
    if request.is_ajax():
        q = request.GET.get('q')
        gid = request.GET.get('gid')

        if gid:
            gid = gid
        else:
            gid = None

        if q is not None:
            purchases = PurchaseProduct.objects.filter(
                Q(invoice_number__icontains=q) |
                Q(stock__variant__product__name__icontains=q) |
                Q(created__icontains=q) |
                Q(supplier__name__icontains=q)).order_by('id')
            all_purchases = 0
            for purchase in purchases:
                all_purchases += purchase.get_total_cost()

            if gid:
                purchases = purchases.filter(created__icontains=gid)

            data = {
                'today': date.today(),
                "purchases": purchases,
                'puller': request.user,
                'gid': gid
            }
            pdf = render_to_pdf('dashboard/reports/purchase/pdf/pdf.html', data)
            return HttpResponse(pdf, content_type='application/pdf')
        else:
            purchases = PurchaseProduct.objects.all().order_by('id')
            all_purchases = 0
            for purchase in purchases:
                all_purchases += purchase.get_total_cost()

            if gid:
                purchases = purchases.filter(created__icontains=gid)

            data = {
                'today': date.today(),
                "purchases": purchases,
                'puller': request.user,
                'gid': gid
            }
            pdf = render_to_pdf('dashboard/reports/purchase/pdf/pdf.html', data)
            return HttpResponse(pdf, content_type='application/pdf')


@staff_member_required
def purchase_export_csv(request):
    if request.is_ajax():
        q = request.GET.get('q')
        gid = request.GET.get('gid')

        if gid:
            gid = gid
        else:
            gid = None

        if q is not None:
            purchases = PurchaseProduct.objects.filter(
                Q(invoice_number__icontains=q) |
                Q(stock__variant__product__name__icontains=q) |
                Q(created__icontains=q) |
                Q(supplier__name__icontains=q)).order_by('id')
            if gid:
                purchases = purchases.filter(created__icontains=gid)
        else:
            purchases = PurchaseProduct.objects.all().order_by('id')
            if gid:
                purchases = purchases.filter(created__icontains=gid)

        pdfname = 'products' + str(random.random())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="' + pdfname + '.csv"'
        # qs = PurchaseProduct.objects.all().order_by('id')
        qs = purchases
        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
        if gid:
            writer.writerow([
                smart_str(''),
                smart_str(''),
                smart_str(''),
                smart_str(''),
                smart_str(''),
                smart_str(''),
            ])
            writer.writerow([
                smart_str(''),
                smart_str(''),
                smart_str(u"Purchase Date"),
                smart_str('09-08-2017'),
                smart_str(''),
                smart_str(''),
            ])
        writer.writerow([
            smart_str(u"Transaction Date"),
            smart_str(u"Supplier Name"),
            smart_str(u"Item Name"),
            smart_str(u"Unit Cost"),
            smart_str(u"Quantity (unit)"),
            smart_str(u"Total Purchase"),
        ])

        for obj in qs:
            writer.writerow([
                smart_str(obj.created),
                smart_str(obj.supplier),
                smart_str(obj.stock.variant.display_product()),
                smart_str(obj.stock.variant.get_price_per_item().gross),
                smart_str(obj.quantity),
                smart_str(obj.get_total_cost()),
            ])
        return response
