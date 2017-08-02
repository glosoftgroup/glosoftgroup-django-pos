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

from . import forms
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
def view(request):
	try:
		queryset_list = Product.objects.all()
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
		user_trail(request.user.name, 'accessed the roles page','view')
		info_logger.info('User: '+str(request.user.name)+' accessed the roles page page')
		product_classes = ProductClass.objects.all()

		product_class = ProductClass()
		form = forms.ProductClassForm(request.POST or None,
									  instance=product_class)
		data = {
			'product_classes':product_classes,
			'product_results': product_results,
			'totalp':paginator.num_pages,
		    'form':form,
			'product_class':product_class,
			'hello':'hello'
		}
		if request.GET.get('initial'):
			return HttpResponse(paginator.num_pages)
		else:
			return TemplateResponse(request, 'dashboard/product/roles/view.html', data)
	except TypeError as e:
		error_logger.error(e)
		return HttpResponse('error accessing users')

def paginate(request):
	page = int(request.GET.get('page', 1))
	list_sz = request.GET.get('size')
	p2_sz = request.GET.get('psize')
	select_sz = request.GET.get('select_size')

	try:
		queryset_list = Product.objects.all()
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
		return TemplateResponse(request, 'dashboard/product/roles/paginate.html', {'product_results': product_results})
	except Exception, e:
		return  HttpResponse()


@staff_member_required
def product_filter(request):
	queryset_list = Product.objects.all()
	#paginator = Paginator(queryset_list, 10)
	page = request.GET.get('page',1)
	size = request.GET.get('size',10)
	search = request.GET.get('search_text','')
	if search != '' and search != None:
		queryset_list = Product.objects.filter(
		   Q(name__icontains=search)|
		   Q(variants__sku__icontains=search)|
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
	ctx = {'products_count': products_count,'product_results': product_results,'search_count':len(product_results)}
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
				return TemplateResponse(request, 'dashboard/product/roles/paginate.html', {'product_results': product_results})

			return TemplateResponse(request, 'dashboard/product/roles/search.html',
									{'product_results':product_results, 'pn': paginator.num_pages, 'sz': sz, 'q': q})