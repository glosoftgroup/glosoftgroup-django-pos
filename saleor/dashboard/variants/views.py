from __future__ import unicode_literals

import emailit.api
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.utils.translation import pgettext_lazy
from django.views.decorators.http import require_http_methods
from django.contrib.postgres.search import SearchVector

from ...core.utils import get_paginator_items
from ...purchase.models import (
                                PurchaseOrder,
                                PurchaseItems,
                                PurchaseProduct
                                )
from ...supplier.models import Supplier
from ...product.models import (Product, ProductAttribute, Category,
                               ProductClass, AttributeChoiceValue,
                               ProductImage, ProductVariant, Stock,
                               StockLocation, ProductTax, StockHistoryEntry)
from ..views import staff_member_required
from ..views import get_low_stock_products
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ...decorators import permission_decorator, user_trail
import logging

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
def stock_pages(request):
    queryset_list = ProductVariant.objects.all()
    size = request.GET.get('size',10)
    page = request.GET.get('page',1)
    search = str(request.GET.get('search_text',''))
    if search != '' and search != None:
        queryset_list = ProductVariant.objects.filter(
            Q(sku__icontains=search) |
            Q(product__name__icontains=search)
            ).order_by('-id') 
    paginator = Paginator(queryset_list,int(size)) # Show 10 contacts per page
    
    try:
        queryset = paginator.page(int(page))
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)
    return HttpResponse(paginator.num_pages)

@staff_member_required
def variant_list(request,pk=None):
    try:
        if pk:
            product = Product.objects.get(pk=int(pk))
            product_results = ProductVariant.objects.filter(product=product).order_by('-id')      
        else:
            product_results = ProductVariant.objects.all().order_by('-id')      
        page = request.GET.get('page', 1)
        categories = Category.objects.all()
        paginator = Paginator(product_results, 10)
        try:
            product_results = paginator.page(page)
        except PageNotAnInteger:
            product_results = paginator.page(1)
        except InvalidPage:
            product_results = paginator.page(1)
        except EmptyPage:
            product_results = paginator.page(paginator.num_pages)        
        return TemplateResponse(request, 'dashboard/variants/variant_list.html', 
                        {'product_results':product_results,
                        'categories':categories,
                        'pn':paginator.num_pages,
                        'pk':pk,
                        'product':product
                        })
    except TypeError as e:
        error_logger.error(e)
        return HttpResponse('error accessing users')

@staff_member_required
def variant_paginate(request,pk=None):
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    if request.GET.get('gid'):
        if pk:
            product = Product.objects.filter(pk=int(pk))
            product_results = ProductVariant.objects.filter(product__categories=request.GET.get('gid'),pk=int(pk))
        else:
            product_results = ProductVariant.objects.filter(product__categories=request.GET.get('gid'))
        if p2_sz:
            paginator = Paginator(product_results, int(p2_sz))
            product_results = paginator.page(page)
            return TemplateResponse(request,'dashboard/purchase/paginate.html',
                   {'product_results':product_results,
                   'product':product})

        paginator = Paginator(product_results, 10)
        product_results = paginator.page(page)
        return TemplateResponse(request,
               'dashboard/purchase/p2.html',
               {'product_results':product_results, 
                'pn':paginator.num_pages,'sz':10,
                'gid':request.GET.get('gid'),
                'product':product
                })

    else:
        if pk:
            product_results = ProductVariant.objects.filter(pk=int(pk)).order_by('-id')
        else:
            product_results = ProductVariant.objects.all().order_by('-id')
        if list_sz:
            paginator = Paginator(product_results, int(list_sz))
            product_results = paginator.page(page)
            print product_results
            print 'sdflsdjflsdjf'
            return TemplateResponse(request,'dashboard/purchase/p2.html',{'product_results':product_results, 'pn':paginator.num_pages,'sz':list_sz, 'gid':0})
        else:
            paginator = Paginator(product_results, 10)
        if p2_sz:
            paginator = Paginator(product_results, int(p2_sz))
            product_results = paginator.page(page)
            return TemplateResponse(request,'dashboard/purchase/paginate.html',{'product_results':product_results})

        try:
            product_results = paginator.page(page)
        except PageNotAnInteger:
            product_results = paginator.page(1)
        except InvalidPage:
            groups = paginator.page(1)
        except EmptyPage:
            product_results = paginator.page(paginator.num_pages)
        return TemplateResponse(request,'dashboard/purchase/paginate.html',{'product_results':product_results,'pk':pk})


@staff_member_required
def variant_search( request,pk=None ):    
    if request.is_ajax():
        page = request.GET.get('page', 1)
        list_sz = request.GET.get('size',10)
        p2_sz = request.GET.get('psize')
        q = request.GET.get( 'q' )
        if list_sz is None:
            sz = 10
        else:
            sz = list_sz
        if q is not None:
            if pk:
                product_results = ProductVariant.objects.filter(pk=int(pk)).filter( 
                Q(sku__icontains=q) |
                Q(product__name__icontains=q)).order_by('-id')
            else:            
                product_results = ProductVariant.objects.filter( 
                Q(sku__icontains=q) |
                Q(product__name__icontains=q)).order_by('-id')
            paginator = Paginator(product_results, 10)
            try:
                product_results = paginator.page(page)
            except PageNotAnInteger:
                product_results = paginator.page(1)
            except InvalidPage:
                product_results = paginator.page(1)
            except EmptyPage:
                product_results = paginator.page(paginator.num_pages)
            if p2_sz:
                product_results = paginator.page(page)
                return TemplateResponse(request,'dashboard/purchase/paginate.html',{'product_results':product_results})

            return TemplateResponse(request, 'dashboard/purchase/search.html', {'product_results':product_results, 'pn':paginator.num_pages,'sz':sz,'q':q})

@staff_member_required
def stock_filter(request):
    queryset_list = ProductVariant.objects.all()
    #paginator = Paginator(queryset_list, 10)
    page = request.GET.get('page',1)
    size = request.GET.get('size',10)
    search = request.GET.get('search_text','')
    if search != '' and search != None:
        queryset_list = ProductVariant.objects.filter(
            Q(sku__icontains=search) |
            Q(product__name__icontains=search)
            ).order_by('-id')            
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
    ctx = {'pn':paginator.num_pages,'products_count': products_count,'product_results': product_results,'search_count':len(product_results)}
    return TemplateResponse(
    request, 'dashboard/includes/sku_search_results.html',
    ctx)
