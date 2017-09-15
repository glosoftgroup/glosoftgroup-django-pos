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
# from django.template.defaultfilters import date
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
import datetime
from datetime import date, timedelta
from django.utils.dateformat import DateFormat
import logging

from ...decorators import permission_decorator, user_trail
from ...utils import render_to_pdf
import csv
import random
from django.utils.encoding import smart_str
from datetime import date

from ...core.utils import get_paginator_items
from ..views import staff_member_required
from ...userprofile.models import User
from ...customer.models import Customer
from ...sale.models import Sales, SoldItem, DrawerCash
from ...product.models import Product, ProductVariant
from ...purchase.models import PurchaseProduct
from ...decorators import permission_decorator, user_trail
from ...dashboard.views import get_low_stock_products

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
def sales_paginate(request):
	page = int(request.GET.get('page'))
	pk = int(request.GET.get('cpk'))
	list_sz = request.GET.get('size')
	date = request.GET.get('date')
	action = request.GET.get('action')
	p2_sz = request.GET.get('psize')
	select_sz = request.GET.get('select_size')
	gid = request.GET.get('gid')
	sales = Sales.objects.all().order_by('-id')
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
										 'that_date_sum': that_date_sum, 'date': date, 'today': today, 'customer':customer})

			except ObjectDoesNotExist as e:
				return TemplateResponse(request, 'dashboard/customer/sales/p2.html', {'date': date, 'customer':customer})
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
											{'sales': sales, 'gid': action, 'customer':customer})

				paginator = Paginator(sales, 10)
				sales = paginator.page(page)
				return TemplateResponse(request, 'dashboard/customer/sales/p2.html',
										{'sales': sales, 'pn': paginator.num_pages, 'sz': 10, 'gid': action,
										 'total_sales': total_sales, 'total_tax': total_tax, 'tsum': tsum, 'customer':customer})

			except ObjectDoesNotExist as e:
				return TemplateResponse(request, 'dashboard/customer/sales/p2.html', {'date': date, 'customer':customer})
	else:
		try:
			last_sale = Sales.objects.latest('id')
			last_date_of_sales = DateFormat(last_sale.created).format('Y-m-d')
			all_sales = csales.filter(created__contains=last_date_of_sales)
			total_sales_amount = all_sales.aggregate(Sum('total_net'))
			total_tax_amount = all_sales.aggregate(Sum('total_tax'))
			sales = []
			for sale in all_sales:
				quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
				setattr(sale, 'quantity', quantity['c'])
				sales.append(sale)

			if list_sz:
				paginator = Paginator(sales, int(list_sz))
				sales = paginator.page(page)
				return TemplateResponse(request, 'dashboard/customer/sales/p2.html',
										{'sales': sales, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0,
										 'total_sales': total_sales, 'total_tax': total_tax, 'tsum': tsum, 'customer':customer})
			else:
				paginator = Paginator(sales, 10)
			if p2_sz:
				paginator = Paginator(sales, int(p2_sz))
				sales = paginator.page(page)
				return TemplateResponse(request, 'dashboard/customer/sales/paginate.html', {'sales': sales, 'customer':customer})

			if date:
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
												{'sales': sales, 'gid': date, 'customer':customer})

					paginator = Paginator(sales, 10)
					sales = paginator.page(page)
					return TemplateResponse(request, 'dashboard/customer/sales/p2.html',
											{'sales': sales, 'pn': paginator.num_pages, 'sz': 10, 'gid': date,
											 'total_sales': total_sales, 'total_tax': total_tax, 'tsum': tsum,
											 'that_date_sum': that_date_sum, 'date': date, 'today': today, 'customer':customer})

				except ObjectDoesNotExist as e:
					return TemplateResponse(request, 'dashboard/customer/sales/p2.html', {'date': date, 'customer':customer})

			try:
				sales = paginator.page(page)
			except PageNotAnInteger:
				sales = paginator.page(1)
			except InvalidPage:
				sales = paginator.page(1)
			except EmptyPage:
				sales = paginator.page(paginator.num_pages)
			return TemplateResponse(request, 'dashboard/customer/sales/paginate.html', {'sales': sales, 'customer':customer})
		except ObjectDoesNotExist as e:
			return TemplateResponse(request, 'dashboard/customer/sales/p2.html', {'date': date, 'customer':customer})


@staff_member_required
def sales_search(request):
	if request.is_ajax():
		pk = int(request.GET.get('cpk'))
		page = request.GET.get('page', 1)
		list_sz = request.GET.get('size', 10)
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
				Q(user__name__icontains=q)).order_by('id')
			sales = []
			for sale in all_sales:
				quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
				setattr(sale, 'quantity', quantity['c'])
				sales.append(sale)
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
				return TemplateResponse(request, 'dashboard/customer/sales/paginate.html', {'sales': sales, 'customer':customer})

			return TemplateResponse(request, 'dashboard/customer/sales/search.html',
									{'sales': sales, 'pn': paginator.num_pages, 'sz': sz, 'q': q, 'customer':customer})
