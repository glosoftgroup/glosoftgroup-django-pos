from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.utils.translation import pgettext_lazy
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count, Min, Sum, Avg, Max
from django.core import serializers
from django.template.defaultfilters import date
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
import datetime
from datetime import date, timedelta
from django.utils.dateformat import DateFormat
import logging

from ..views import staff_member_required
from ...core.utils import get_paginator_items
from ...userprofile.models import User
from ...sale.models import Sales, SoldItem
from ...product.models import Product, ProductVariant
from ...decorators import permission_decorator, user_trail
from ...utils import render_to_pdf, convert_html_to_pdf, image64

@staff_member_required
def sales_margin(request):
	get_date = request.GET.get('date')
	pdf = request.GET.get('pdf')
	image = request.GET.get('image')
	jax = request.GET.get('ajax')

	dateFrom = request.GET.get('dateFrom')
	dateTo = request.GET.get('dateTo')

	today = datetime.datetime.now()
	if get_date:
		date = get_date
		date2 = request.GET.get('date2')
	elif dateFrom and dateTo:
		x = []
		a, b, c = dateFrom.split('-')
		x.append(c)
		x.append(b)
		x.append(a)
		dateFrom2 = '-'.join(x)
		y = []
		d, e, f = dateTo.split('-')
		y.append(f)
		y.append(e)
		y.append(d)
		dateTo2 = '-'.join(y)

		z = []
		g, h, i = dateTo.split('-')
		z.append(g)
		if i == '30':
			z.append(h)
			z.append(str(int(i) + 1))
		elif i =='31':
			z.append(str(int(h) + 1))
			z.append('01')
		else:
			z.append(h)
			z.append(str(int(i) + 1))
		dateTo = '-'.join(z)
		date2 = dateFrom2 + ' - ' + dateTo2
	else:
		try:
			last_sale = Sales.objects.latest('id')
			date = DateFormat(last_sale.created).format('Y-m-d')
			date2 = DateFormat(last_sale.created).format('d/m/Y')
		except:
			date = DateFormat(datetime.datetime.today()).format('Y-m-d')
			date2 = DateFormat(datetime.datetime.today()).format('d/m/Y')

	try:
		if dateFrom and dateTo:
			sales = Sales.objects.filter(created__range=[str(dateFrom), str(dateTo)])
			soldItems = SoldItem.objects.filter(sales__created__range=[str(dateFrom), str(dateTo)]).order_by('-id')
			totalSales = sales.aggregate(Sum('total_net'))['total_net__sum']
			totalTax = sales.aggregate(Sum('total_tax'))['total_tax__sum']
		else:
			sales = Sales.objects.filter(created__icontains=date).order_by('-id')
			soldItems = SoldItem.objects.filter(sales__created__icontains=date).order_by('-id')
			totalSales = sales.aggregate(Sum('total_net'))['total_net__sum']
			totalTax = sales.aggregate(Sum('total_tax'))['total_tax__sum']



		costPrice = []
		for i in soldItems:
			product = ProductVariant.objects.get(sku=i.sku)
			try:
				quantity = product.get_cost_price().gross
			except:
				quantity = product.get_cost_price()
			costPrice.append(quantity)

		totalCostPrice = sum(costPrice)
		try:
			grossProfit = totalSales - totalCostPrice
			status = 'true'
			margin = round((grossProfit / totalSales) * 100, 2)
			try:
				markup = round((grossProfit / totalCostPrice) * 100, 2)
			except:
				markup = round(0, 2)
		except:
			grossProfit = 0
			margin = 0
			markup = 0
			status = 'false'

		img = image64()
		data = {
			'totalCostPrice':totalCostPrice,
			'totalSales':totalSales,
			'totalTax':totalTax,
			'grossProfit':grossProfit,
			'markup':markup,
			'margin':margin,
			'date':date2,
			'status':status,
			'puller':request.user,
			'image': img,
			'reportImage':image
		}
		if pdf:
			pdf = render_to_pdf('dashboard/reports/sales_profit/pdf.html', data)
			return HttpResponse(pdf, content_type='application/pdf')
		elif jax:
			return TemplateResponse(request, 'dashboard/reports/sales_profit/ajax.html', data)
		else:
			return TemplateResponse(request, 'dashboard/reports/sales_profit/profit.html', data)
	except Exception, e:
		data = {
			'status': 'false',
			'date':date2
		}
		if jax:
			return TemplateResponse(request, 'dashboard/reports/sales_profit/ajax.html', data)
		else:
			return TemplateResponse(request, 'dashboard/reports/sales_profit/profit.html', data)

@staff_member_required
def sales_tax(request):
	get_date = request.GET.get('date')
	pdf = request.GET.get('pdf')
	image = request.GET.get('image')
	jax = request.GET.get('ajax')

	dateFrom = request.GET.get('dateFrom')
	dateTo = request.GET.get('dateTo')

	today = datetime.datetime.now()
	if get_date:
		date = get_date
		date2 = request.GET.get('date2')
	elif dateFrom and dateTo:
		x = []
		a, b, c = dateFrom.split('-')
		x.append(c)
		x.append(b)
		x.append(a)
		dateFrom2 = '-'.join(x)
		y = []
		d, e, f = dateTo.split('-')
		y.append(f)
		y.append(e)
		y.append(d)
		dateTo2 = '-'.join(y)

		z = []
		g, h, i = dateTo.split('-')
		z.append(g)
		if i == '30':
			z.append(h)
			z.append(str(int(i) + 1))
		elif i =='31':
			z.append(str(int(h) + 1))
			z.append('01')
		else:
			z.append(h)
			z.append(str(int(i) + 1))
		dateTo = '-'.join(z)
		date2 = dateFrom2 + ' - ' + dateTo2
	else:
		try:
			last_sale = Sales.objects.latest('id')
			date = DateFormat(last_sale.created).format('Y-m-d')
			date2 = DateFormat(last_sale.created).format('d/m/Y')
		except:
			date = DateFormat(datetime.datetime.today()).format('Y-m-d')
			date2 = DateFormat(datetime.datetime.today()).format('d/m/Y')

	try:
		if dateFrom and dateTo:
			sales = Sales.objects.filter(created__range=[str(dateFrom), str(dateTo)])
			soldItems = SoldItem.objects.filter(sales__created__range=[str(dateFrom), str(dateTo)]).order_by('-id')
			totalSales = sales.aggregate(Sum('total_net'))['total_net__sum']
			totalSalesTax = sales.aggregate(Sum('total_tax'))['total_tax__sum']
		else:
			sales = Sales.objects.filter(created__icontains=date).order_by('-id')
			soldItems = SoldItem.objects.filter(sales__created__icontains=date).order_by('-id')
			totalSales = sales.aggregate(Sum('total_net'))['total_net__sum']
			totalSalesTax = sales.aggregate(Sum('total_tax'))['total_tax__sum']



		costPrice = []
		for i in soldItems:
			product = ProductVariant.objects.get(sku=i.sku)
			try:
				cost = product.get_cost_price().gross
			except Exception,e:
				cost = product.get_cost_price()
			except Exception,e:
				cost = 0
			costPrice.append(cost)

		totalCost = sum(costPrice)
		if totalCost == 0:
			totalCostTax = 0
		else:
			totalCostTax = round((totalCost-((totalCost*100))/116), 2)
		taxDiff = totalSalesTax - totalCostTax

		img = image64()
		data = {
			'totalCostTax':totalCostTax,
			'totalSalesTax':totalSalesTax,
			'taxDiff':taxDiff,
			'date':date2,
			'status':'true',
			'puller':request.user,
			'image': img,
			'reportImage':image
		}
		if pdf:
			pdf = render_to_pdf('dashboard/reports/sales_tax/pdf.html', data)
			return HttpResponse(pdf, content_type='application/pdf')
		elif jax:
			return TemplateResponse(request, 'dashboard/reports/sales_tax/ajax.html', data)
		else:
			return TemplateResponse(request, 'dashboard/reports/sales_tax/tax.html', data)
	except Exception, e:
		data = {
			'status': 'false',
			'date':date2
		}
		print (e)
		if jax:
			return TemplateResponse(request, 'dashboard/reports/sales_tax/ajax.html', data)
		else:
			return TemplateResponse(request, 'dashboard/reports/sales_tax/tax.html', data)