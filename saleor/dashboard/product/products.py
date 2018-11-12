from __future__ import unicode_literals
from django.template.response import TemplateResponse
from . import forms
from ...product.models import (Product, ProductClass)
from ..views import staff_member_required
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ...decorators import user_trail
from ...utils import render_to_pdf, default_logo
import csv
import random
from django.utils.encoding import smart_str
from datetime import date

from structlog import get_logger

logger = get_logger(__name__)


@staff_member_required
def view(request):
    try:
        queryset_list = Product.objects.all().order_by('-id')
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
        product_results = queryset_list
        user_trail(request.user.name, 'accessed the roles page', 'view')
        logger.info('User: ' + str(request.user.name) + ' accessed the roles page page')
        product_classes = ProductClass.objects.all()

        product_class = ProductClass()
        form = forms.ProductClassForm(request.POST or None,
                                      instance=product_class)
        data = {
            'product_classes': product_classes,
            'product_results': product_results,
            'totalp': paginator.num_pages,
            'form': form,
            'product_class': product_class,
            'hello': 'hello'
        }
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/product/roles/view.html', data)
    except TypeError as e:
        logger.error(e)
        return HttpResponse('error accessing users')


def paginate(request):
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')

    try:
        queryset_list = Product.objects.all().order_by('-id')
        if list_sz:
            paginator = Paginator(queryset_list, int(list_sz))
            queryset_list = paginator.page(page)
            product_results = queryset_list
            data = {
                'product_results': product_results,
                'pn': paginator.num_pages,
                'sz': list_sz,
                'gid': 0
            }
            return TemplateResponse(request, 'dashboard/product/roles/p2.html', data)
        else:
            paginator = Paginator(queryset_list, 10)
            if p2_sz:
                paginator = Paginator(queryset_list, int(p2_sz))
            queryset_list = paginator.page(page)
            product_results = queryset_list
            data = {
                'product_results': product_results,
                'sz': p2_sz
            }
            return TemplateResponse(request, 'dashboard/product/roles/paginate.html', data)

        try:
            queryset_list = paginator.page(page)
        except PageNotAnInteger:
            queryset_list = paginator.page(1)
        except InvalidPage:
            queryset_list = paginator.page(1)
        except EmptyPage:
            queryset_list = paginator.page(paginator.num_pages)
        product_results = queryset_list
        return TemplateResponse(request, 'dashboard/product/roles/paginate.html',
                                {'product_results': product_results, 'sz': p2_sz})
    except Exception, e:
        return HttpResponse()


@staff_member_required
def product_filter(request):
    queryset_list = Product.objects.all().order_by('-id')
    # paginator = Paginator(queryset_list, 10)
    page = request.GET.get('page', 1)
    size = request.GET.get('size', 10)
    search = request.GET.get('search_text', '')
    if search != '' and search != None:
        queryset_list = Product.objects.filter(
            Q(name__icontains=search) |
            Q(variants__sku__icontains=search) |
            Q(categories__name__icontains=search)
        ).order_by('-id').distinct()
    paginator = Paginator(queryset_list, int(size))
    products_count = len(queryset_list)
    try:
        queryset = paginator.page(int(page))
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)
    product_results = queryset
    ctx = {'products_count': products_count, 'product_results': product_results, 'search_count': len(product_results)}
    return TemplateResponse(
        request, 'dashboard/includes/product_search_results.html',
        ctx)


@staff_member_required
def search(request):
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
            queryset_list = Product.objects.filter(
                Q(name__icontains=q) |
                Q(variants__sku__icontains=q) |
                Q(categories__name__icontains=q)).order_by('-id').distinct()
            paginator = Paginator(queryset_list, 10)

            try:
                queryset_list = paginator.page(page)
            except PageNotAnInteger:
                queryset_list = paginator.page(1)
            except InvalidPage:
                queryset_list = paginator.page(1)
            except EmptyPage:
                queryset_list = paginator.page(paginator.num_pages)
            product_results = queryset_list
            if p2_sz:
                queryset_list = paginator.page(page)
                return TemplateResponse(request, 'dashboard/product/roles/paginate.html',
                                        {'product_results': product_results})

            return TemplateResponse(request, 'dashboard/product/roles/search.html',
                                    {'product_results': product_results, 'pn': paginator.num_pages, 'sz': sz, 'q': q})


@staff_member_required
def products_pdf(request):
    product_results = Product.objects.all()
    img = default_logo()
    data = {
        'today': date.today(),
        'product_results': product_results,
        'puller': request.user,
        'image': img,
    }
    pdf = render_to_pdf('dashboard/product/roles/pdf/pdf.html', data)
    return HttpResponse(pdf, content_type='application/pdf')


@staff_member_required
def products_export_csv(request):
    pdfname = 'products' + str(random.random())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + pdfname + '.csv"'
    qs = Product.objects.all()
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(u"ID"),
        smart_str(u"Product Name"),
        smart_str(u"Category"),
        smart_str(u"Price"),
        smart_str(u"Current Stock"),
    ])
    for obj in qs:
        writer.writerow([
            smart_str(obj.pk),
            smart_str(obj.name),
            smart_str(obj.get_first_category()),
            smart_str(obj.price.gross),
            smart_str(obj.get_variants_count()),
        ])
    return response
