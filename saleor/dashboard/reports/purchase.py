from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.utils.translation import pgettext_lazy
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count, Min, Sum, Avg, F, Q
from django.core import serializers
from django.template.defaultfilters import date
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
import datetime
from datetime import date, timedelta
from django.utils.dateformat import DateFormat
import logging

from ...core.utils import get_paginator_items
from ..views import staff_member_required
from ...userprofile.models import User
from ...sale.models import Sales, SoldItem, DrawerCash
from ...product.models import Product, ProductVariant
from ...purchase.models import PurchaseProduct
from ...decorators import permission_decorator, user_trail
from ...dashboard.views import get_low_stock_products

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
@permission_decorator('reports.view_purchase_reports')
def purchase_reports(request):
	try:
		queryset_list = PurchaseProduct.objects.all().order_by('id')
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
		user_trail(request.user.name, 'accessed the purchase reports page','view')
		info_logger.info('User: '+str(request.user.name)+' accessed the purchase reports page page')

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
		error_logger.error(e)
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
				"gid": date,'pn': paginator.num_pages, 'sz': 10, 'gid': date,
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
				'all_purchases':total_purchases,
				'purchases': purchases,
				'pn': paginator.num_pages,
				'sz': list_sz, 'gid': 0
			}
			return TemplateResponse(request,'dashboard/reports/purchase/p2.html',ctx)
		else:
			paginator = Paginator(purchases, 10)
		if p2_sz:
			paginator = Paginator(purchases, int(p2_sz))
			purchases = paginator.page(page)
			return TemplateResponse(request,'dashboard/reports/purchase/paginate.html',{'purchases':purchases})

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

		return TemplateResponse(request,'dashboard/reports/purchase/paginate.html',data)
	except Exception, e:
		error_logger.error(e)

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

				return TemplateResponse(request, 'dashboard/reports/purchase/paginate.html', {'purchases': purchases})
			data = {
				"purchases": purchases,
				"all_purchases": all_purchases,
				"gid": date, 'pn': paginator.num_pages, 'sz': sz, 'q': q,
			}
			return TemplateResponse(request, 'dashboard/reports/purchase/search.html',data)

