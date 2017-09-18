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
import random
import csv
from django.utils.encoding import smart_str
from decimal import Decimal
from calendar import monthrange
import calendar
from django_xhtml2pdf.utils import generate_pdf

import re
import base64

from ...core.utils import get_paginator_items
from ..views import staff_member_required
from ...userprofile.models import User
from ...sale.models import Sales, SoldItem, Terminal
from ...credit.models import Credit, CreditedItem
from ...product.models import Product, ProductVariant, Category
from ...decorators import permission_decorator, user_trail
from ...utils import render_to_pdf, convert_html_to_pdf, image64

from .hours_chart import get_item_results, get_terminal_results, get_user_results, get_hours_results, get_hours_results_range, get_date_results_range, get_date_results, get_category_results

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

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
		'image':ImageData
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


	pdfname = 'users'+str(random.random())
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="'+pdfname+'.csv"'
	qs = User.objects.all()
	writer = csv.writer(response, csv.excel)
	response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
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
def sales_list_pdf( request ):

	if request.is_ajax():
		q = request.GET.get( 'q' )
		gid = request.GET.get('gid')

		if gid:
			gid = gid
		else:
			gid = None

		sales = []
		if q is not None:
			all_sales = Credit.objects.filter(
				Q(invoice_number__icontains=q) |
				Q(terminal__terminal_name__icontains=q) |
				Q(created__icontains=q) |
				Q(customer__name__icontains=q) | Q(customer__mobile__icontains=q) |
				Q(credititems__product_name__icontains=q) |
				Q(user__email__icontains=q) |
				Q(user__name__icontains=q)).order_by('id').distinct()

			if gid:
				csales = all_sales.filter(created__icontains=gid)
				for sale in csales:
					quantity = CreditedItem.objects.filter(credit=sale).aggregate(c=Count('sku'))
					setattr(sale, 'quantity', quantity['c'])
					sales.append(sale)
			else:
				for sale in all_sales:
					quantity = CreditedItem.objects.filter(credit=sale).aggregate(c=Count('sku'))
					setattr(sale, 'quantity', quantity['c'])
					sales.append(sale)

		elif gid:
			csales = Credit.objects.filter(created__icontains=gid)
			for sale in csales:
				quantity = CreditedItem.objects.filter(credit=sale).aggregate(c=Count('sku'))
				setattr(sale, 'quantity', quantity['c'])
				sales.append(sale)
		else:
			try:
				last_sale = Credit.objects.latest('id')
				gid = DateFormat(last_sale.created).format('Y-m-d')
			except:
				gid = DateFormat(datetime.datetime.today()).format('Y-m-d')

			csales = Credit.objects.filter(created__icontains=gid)
			for sale in csales:
				quantity = CreditedItem.objects.filter(credit=sale).aggregate(c=Count('sku'))
				setattr(sale, 'quantity', quantity['c'])
				sales.append(sale)

		img = image64()
		data = {
			'today': date.today(),
			'sales': sales,
			'puller': request.user,
			'image': img,
			'gid':gid
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
		pdf = render_to_pdf('dashboard/reports/credit/pdf/pdf.html',data)
		return HttpResponse(pdf, content_type='application/pdf')
	except ObjectDoesNotExist as e:
		error_logger.error(e)

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
			'category':image,
			'sales_date':sales_date
		}
		print (sales_date)
		pdf = render_to_pdf('dashboard/reports/credit/pdf/category.html',data)
		return HttpResponse(pdf, content_type='application/pdf')
	except ObjectDoesNotExist as e:
		error_logger.error(e)

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
			'category':image,
			'sales_date':sales_date
		}
		print (sales_date)
		pdf = render_to_pdf('dashboard/reports/credit/pdf/items.html',data)
		return HttpResponse(pdf, content_type='application/pdf')
	except ObjectDoesNotExist as e:
		error_logger.error(e)

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
			'category':image,
			'sales_date':sales_date
		}
		print (sales_date)
		pdf = render_to_pdf('dashboard/reports/credit/pdf/user.html',data)
		return HttpResponse(pdf, content_type='application/pdf')
	except ObjectDoesNotExist as e:
		error_logger.error(e)

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
			'category':image,
			'sales_date':sales_date
		}
		print (sales_date)
		pdf = render_to_pdf('dashboard/reports/credit/pdf/till.html',data)
		return HttpResponse(pdf, content_type='application/pdf')
	except ObjectDoesNotExist as e:
		error_logger.error(e)
