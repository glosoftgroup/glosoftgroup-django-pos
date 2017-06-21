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
from django.db.models import Count, Min, Sum, Avg
from django.core import serializers
from django.template.defaultfilters import date
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Q
import datetime
from django.utils.dateformat import DateFormat
import logging

from ...core.utils import get_paginator_items
from ..views import staff_member_required
from ...userprofile.models import User
from ...sale.models import Sales, SoldItem
from ...product.models import Product, ProductVariant
from ...decorators import permission_decorator, user_trail

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
# @permission_required('userprofile.view_user', raise_exception=True)
def sales_reports(request):
	try:
		today = datetime.date.today()
		items = SoldItem.objects.all().order_by('-id')
		ts = Sales.objects.filter(created__icontains=today)
		tsum = ts.aggregate(Sum('total_net'))
		total_sales = Sales.objects.aggregate(Sum('total_net'))
		total_tax = Sales.objects.aggregate(Sum('total_tax'))
		page = request.GET.get('page', 1)
		paginator = Paginator(items, 10)
		try:
			items = paginator.page(page)
		except PageNotAnInteger:
			items = paginator.page(1)
		except InvalidPage:
			items = paginator.page(1)
		except EmptyPage:
			items = paginator.page(paginator.num_pages)
		user_trail(request.user.name, 'accessed sales reports','view')
		info_logger.info('User: '+str(request.user.name)+' accessed the view sales report page')
		if request.GET.get('initial'):
			return HttpResponse(paginator.num_pages)
		else:
			return TemplateResponse(request, 'dashboard/reports/sales/sales.html', {'items':items, 'total_sales':total_sales,'total_tax':total_tax, 'ts':ts, 'tsum':tsum})
	except TypeError as e:
		error_logger.error(e)
		return HttpResponse('error accessing sales reports')

def sales_paginate(request):
	page = int(request.GET.get('page'))
	list_sz = request.GET.get('size')
	date = request.GET.get('date')
	action = request.GET.get('action')
	p2_sz = request.GET.get('psize')
	select_sz = request.GET.get('select_size')
	gid = request.GET.get('gid')
	items = SoldItem.objects.all().order_by('-id')
	today_formart = DateFormat(datetime.date.today())
	today = today_formart.format('Y-m-d')
	ts = Sales.objects.filter(created__icontains=today)
	tsum = ts.aggregate(Sum('total_net'))
	total_sales = Sales.objects.aggregate(Sum('total_net'))
	total_tax = Sales.objects.aggregate(Sum('total_tax'))

	if request.GET.get('sth'):

		if date:
			try:
				items = SoldItem.objects.filter(sales__created__icontains=date).order_by('-id')
				that_date = Sales.objects.filter(created__icontains=date)
				that_date_sum = that_date.aggregate(Sum('total_net'))
				if p2_sz and gid:
					paginator = Paginator(items, int(p2_sz))
					items = paginator.page(page)
					return TemplateResponse(request,'dashboard/reports/sales/paginate.html',{'items':items, 'gid':date})

				paginator = Paginator(items, 10)
				items = paginator.page(page)
				return TemplateResponse(request,'dashboard/reports/sales/p2.html',
					{'items':items, 'pn':paginator.num_pages,'sz':10,'gid':date,
					'total_sales':total_sales,'total_tax':total_tax,'tsum':tsum, 
					'that_date_sum':that_date_sum, 'date':date, 'today':today})

			except ValueError as e:
				return HttpResponse(e)
		if action:
			try:
				# items = SoldItem.objects.filter(date=date).order_by('-id')
				items = SoldItem.objects.filter(sales__created__icontains=date).order_by('-id')
				if p2_sz and gid:
					paginator = Paginator(items, int(p2_sz))
					items = paginator.page(page)
					return TemplateResponse(request,'dashboard/reports/sales/paginate.html',{'items':items, 'gid':action})

				paginator = Paginator(items, 10)
				items = paginator.page(page)
				return TemplateResponse(request,'dashboard/reports/sales/p2.html',
					{'items':items, 'pn':paginator.num_pages,'sz':10,'gid':action, 
					'total_sales':total_sales,'total_tax':total_tax, 'tsum':tsum})

			except ValueError as e:
				return HttpResponse(e)
	else:

		if list_sz:
			paginator = Paginator(items, int(list_sz))
			items = paginator.page(page)
			return TemplateResponse(request,'dashboard/reports/sales/p2.html',{'items':items, 'pn':paginator.num_pages,'sz':list_sz, 'gid':0, 'total_sales':total_sales,'total_tax':total_tax, 'tsum':tsum})
		else:
			paginator = Paginator(items, 10)
		if p2_sz:
			paginator = Paginator(items, int(p2_sz))
			items = paginator.page(page)
			return TemplateResponse(request,'dashboard/reports/sales/paginate.html',{'items':items})

		if date:
			try:
				items = SoldItem.objects.filter(sales__created__icontains=date).order_by('-id')
				that_date = Sales.objects.filter(created__icontains=date)
				that_date_sum = that_date.aggregate(Sum('total_net'))
				if p2_sz:
					paginator = Paginator(items, int(p2_sz))
					items = paginator.page(page)
					return TemplateResponse(request,'dashboard/reports/sales/paginate.html',{'items':items, 'gid':date})

				paginator = Paginator(items, 10)
				items = paginator.page(page)
				return TemplateResponse(request,'dashboard/reports/sales/p2.html',
					{'items':items, 'pn':paginator.num_pages,'sz':10,'gid':date, 
					'total_sales':total_sales,'total_tax':total_tax, 'tsum':tsum, 
					'that_date_sum':that_date_sum, 'date':date, 'today':today})

			except ValueError as e:
				return HttpResponse(e)


		try:
			items = paginator.page(page)
		except PageNotAnInteger:
			items = paginator.page(1)
		except InvalidPage:
			items = paginator.page(1)
		except EmptyPage:
			items = paginator.page(paginator.num_pages)
		return TemplateResponse(request,'dashboard/reports/sales/paginate.html',{'items':items})

def sales_search(request):
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
			items = SoldItem.objects.filter( 
				Q( sku__icontains = q ) |
				Q( product_name__icontains = q ) | 
				Q(sales__created__icontains=q) | 
				Q(sales__user__email__icontains=q)).order_by( 'id' )
			paginator = Paginator(items, 10)
			try:
				items = paginator.page(page)
			except PageNotAnInteger:
				items = paginator.page(1)
			except InvalidPage:
				items = paginator.page(1)
			except EmptyPage:
				items = paginator.page(paginator.num_pages)
			if p2_sz:
				items = paginator.page(page)
				return TemplateResponse(request,'dashboard/reports/sales/paginate.html',{'items':items})

			return TemplateResponse(request, 'dashboard/reports/sales/search.html', {'items':items, 'pn':paginator.num_pages,'sz':sz,'q':q})

def product_reports(request):
	try:
		items = ProductVariant.objects.all().order_by('-id')
		total_sales = ProductVariant.objects.aggregate(Sum('price_override'))
		# total_tax = ProductVariant.objects.aggregate(Sum('product_tax'))
		page = request.GET.get('page', 1)
		paginator = Paginator(items, 10)
		try:
			items = paginator.page(page)
		except PageNotAnInteger:
			items = paginator.page(1)
		except InvalidPage:
			items = paginator.page(1)
		except EmptyPage:
			items = paginator.page(paginator.num_pages)
		user_trail(request.user.name, 'accessed products reports','view')
		info_logger.info('User: '+str(request.user.name)+' accessed the view sales report page')
		if request.GET.get('initial'):
			return HttpResponse(paginator.num_pages)
		else:
			return TemplateResponse(request, 'dashboard/reports/products/products.html', {'items':items, 'total_sales':total_sales})
	except TypeError as e:
		error_logger.error(e)
		return HttpResponse('error accessing products reports')

def products_paginate(request):
	page = int(request.GET.get('page'))
	list_sz = request.GET.get('size')
	date = request.GET.get('date')
	action = request.GET.get('action')
	p2_sz = request.GET.get('psize')
	select_sz = request.GET.get('select_size')
	gid = request.GET.get('gid')
	items = ProductVariant.objects.all().order_by('-id')
	if request.GET.get('sth'):

		# if date:
		# 	try:
		# 		items = ProductVariant.objects.filter(date=date).order_by('-id')
		# 		if p2_sz and gid:
		# 			paginator = Paginator(items, int(p2_sz))
		# 			items = paginator.page(page)
		# 			return TemplateResponse(request,'dashboard/reports/products/paginate.html',{'items':items, 'gid':date})

		# 		paginator = Paginator(items, 10)
		# 		items = paginator.page(page)
		# 		return TemplateResponse(request,'dashboard/reports/products/p2.html',{'items':items, 'pn':paginator.num_pages,'sz':10,'gid':date})

		# 	except ValueError as e:
		# 		return HttpResponse(e)
		if action:
			try:
				items = ProductVariant.objects.filter(date=date).order_by('-id')
				if p2_sz and gid:
					paginator = Paginator(items, int(p2_sz))
					items = paginator.page(page)
					return TemplateResponse(request,'dashboard/reports/products/paginate.html',{'items':items, 'gid':action})

				paginator = Paginator(items, 10)
				items = paginator.page(page)
				return TemplateResponse(request,'dashboard/reports/products/p2.html',{'items':items, 'pn':paginator.num_pages,'sz':10,'gid':action})

			except ValueError as e:
				return HttpResponse(e)
	else:

		if list_sz:
			paginator = Paginator(items, int(list_sz))
			items = paginator.page(page)
			return TemplateResponse(request,'dashboard/reports/products/p2.html',{'items':items, 'pn':paginator.num_pages,'sz':list_sz, 'gid':0})
		else:
			paginator = Paginator(items, 10)
		if p2_sz:
			paginator = Paginator(items, int(p2_sz))
			items = paginator.page(page)
			return TemplateResponse(request,'dashboard/reports/products/paginate.html',{'items':items})

		# if date:
		# 	try:
		# 		items = ProductVariant.objects.filter(updated_at=date).order_by('-id')
		# 		if p2_sz:
		# 			paginator = Paginator(items, int(p2_sz))
		# 			items = paginator.page(page)
		# 			return TemplateResponse(request,'dashboard/reports/products/paginate.html',{'items':items, 'gid':date})

		# 		paginator = Paginator(items, 10)
		# 		items = paginator.page(page)
		# 		return TemplateResponse(request,'dashboard/reports/products/p2.html',{'items':items, 'pn':paginator.num_pages,'sz':10,'gid':date})

		# 	except ValueError as e:
		# 		return HttpResponse(e)


		try:
			items = paginator.page(page)
		except PageNotAnInteger:
			items = paginator.page(1)
		except InvalidPage:
			items = paginator.page(1)
		except EmptyPage:
			items = paginator.page(paginator.num_pages)
		return TemplateResponse(request,'dashboard/reports/products/paginate.html',{'items':items})

def products_search(request):
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
			items = ProductVariant.objects.filter( 
				Q( sku__contains = q ) |
				Q( name__contains = q ) ).order_by( 'id' )
			paginator = Paginator(items, 10)
			try:
				items = paginator.page(page)
			except PageNotAnInteger:
				items = paginator.page(1)
			except InvalidPage:
				items = paginator.page(1)
			except EmptyPage:
				items = paginator.page(paginator.num_pages)
			if p2_sz:
				items = paginator.page(page)
				return TemplateResponse(request,'dashboard/reports/products/paginate.html',{'items':items})

			return TemplateResponse(request, 'dashboard/reports/products/search.html', {'items':items, 'pn':paginator.num_pages,'sz':sz,'q':q})


def purchases_reports(request):
	users = User.objects.all().order_by('id')
	return TemplateResponse(request, 'dashboard/reports/purchase/purchases.html', {'users':users})

def balancesheet_reports(request):
	users = User.objects.all().order_by('id')
	return TemplateResponse(request, 'dashboard/reports/balancesheet/balancesheet.html', {'users':users})

def get_dashboard_data(request):
	label = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]
	default = [12, 19, 3, 5, 2, 3]
	total_sales = Sales.objects.all()
	# total_sales = 
	today = datetime.date.today()
	todays_sales = Sales.objects.filter(created=today).annotate(Sum('total_net'))

	''' get highest product '''
	
	''' get lowest product '''
	data = {
		 "label":label,
		 "default":default,
		 "users":10,
		 "net":serializers.serialize('json', total_sales),
		 "todays_sales": serializers.serialize('json', todays_sales),
	}
	return JsonResponse(data)


#####
##  search using ajax and filter many filds
####

# questions = Help.objects.all()
# filters = {}
# if 'question' in ajax_data:
#     filters['question'] = ajax_data.get('question')
# if 'description' in ajax_data:
#     filters['description'] = ajax_data.get('description')
# if 'status' in ajax_data:
#     filters['status'] = ajax_data.get('status')
# if 'created' in ajax_data:
#     filters['created'] = ajax_data.get('created')
# if 'modified' in ajax_data:
#     filters['modified'] = ajax_data.get('modified')
# questions = questions.filter(**filters).values('id','question','description','status','created','modified').order_by('-id')
