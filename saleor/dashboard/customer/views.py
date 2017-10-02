from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Min, Sum, Avg, F, Q
from ..views import staff_member_required
from ...customer.models import Customer
from ...sale.models import (Sales, SoldItem)
from ...credit.models import Credit
from ...decorators import permission_decorator, user_trail
import logging
import json

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
@permission_decorator('customer.view_customer')
def users(request):
	try:
		users = Customer.objects.all().order_by('-id')
		page = request.GET.get('page', 1)
		paginator = Paginator(users, 10)
		try:
			users = paginator.page(page)
		except PageNotAnInteger:
			users = paginator.page(1)
		except InvalidPage:
			users = paginator.page(1)
		except EmptyPage:
			users = paginator.page(paginator.num_pages)
		user_trail(request.user.name, 'accessed customers page', 'view')
		info_logger.info('User: ' + str(request.user.name) + 'view customers')
		if request.GET.get('initial'):
			return HttpResponse(paginator.num_pages)
		else:
			return TemplateResponse(request, 'dashboard/customer/users.html',{'users': users, 'pn': paginator.num_pages})
	except TypeError as e:
		error_logger.error(e)
		return TemplateResponse(request, 'dashboard/customer/users.html', {'users': users, 'pn': paginator.num_pages})

@staff_member_required
@permission_decorator('customer.add_customer')
def user_add(request):
	try:
		user_trail(request.user.name, 'accessed add customer page', 'view')
		info_logger.info('User: ' + str(request.user.name) + 'accessed add customer page')
		return TemplateResponse(request, 'dashboard/customer/add_user.html',{'permissions':"permissions", 'groups':"groups"})
	except TypeError as e:
		error_logger.error(e)
		return HttpResponse('error accessing add users page')

@staff_member_required
def user_process(request):	
	if request.method == 'POST':
		new_user = Customer()
		if request.POST.get('name'):
			new_user.name = request.POST.get('name')
		if request.POST.get('email'):
			new_user.email = request.POST.get('email')
		if request.POST.get('mobile'):
			new_user.mobile = request.POST.get('mobile').replace(' ','').replace('(','').replace(')','').replace('-','') 		
		if request.POST.get('creditable'):
			new_user.creditable = True
		try:
			new_user.save()
		except:
			error_logger.info('Error when saving ')
		last_id = Customer.objects.latest('id')		
		user_trail(request.user.name, 'created customer: '+str(new_user.name),'add')
		info_logger.info('User: '+str(request.user.name)+' created customer:'+str(new_user.name))
		return HttpResponse(last_id.id)

def user_detail(request, pk):
	user = get_object_or_404(Customer, pk=pk)
	user_trail(request.user.name, 'accessed detail page to view customer: ' + str(user.name), 'view')
	info_logger.info('User: ' + str(request.user.name) + ' accessed detail page to view customer:' + str(user.name))
	return TemplateResponse(request, 'dashboard/customer/detail.html', {'user':user})

def sales_detail(request, pk):
	customer = get_object_or_404(Customer, pk=pk)
	try:
		all_sales = Sales.objects.filter(customer=customer)
		total_sales_amount = all_sales.aggregate(Sum('total_net'))
		total_tax_amount = all_sales.aggregate(Sum('total_tax'))
		total_sales = []
		for sale in all_sales:
			quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
			setattr(sale, 'quantity', quantity['c'])
			total_sales.append(sale)

		page = request.GET.get('page', 1)
		paginator = Paginator(total_sales, 10)
		try:
			total_sales = paginator.page(page)
		except PageNotAnInteger:
			total_sales = paginator.page(1)
		except InvalidPage:
			total_sales = paginator.page(1)
		except EmptyPage:
			total_sales = paginator.page(paginator.num_pages)
		user_trail(request.user.name, 'accessed sales details for customer'+str(customer.name), 'view')
		info_logger.info('User: ' + str(request.user.name) + 'accessed sales details for customer'+str(customer.name))
		if request.GET.get('initial'):
			return HttpResponse(paginator.num_pages)
		else:
			data = {
				'sales': total_sales,
				"total_sales_amount":total_sales_amount,
				"total_tax_amount":total_tax_amount,
				"customer":customer,
				'pn': paginator.num_pages
			}
			return TemplateResponse(request, 'dashboard/customer/sales/sales_list.html',data)
	except ObjectDoesNotExist as e:
		error_logger.error(e)

def sales_items_detail(request, pk=None, ck=None):
	try:
		customer = get_object_or_404(Customer, pk=ck)
		sale = Sales.objects.get(pk=pk)
		items = SoldItem.objects.filter(sales=sale)
		return TemplateResponse(request, 'dashboard/customer/sales/details.html',{'items': items, "sale":sale, "customer":customer})
	except ObjectDoesNotExist as e:
		error_logger.error(e)

@permission_decorator('customer.delete_customer')
def user_delete(request, pk):
	user = get_object_or_404(Customer, pk=pk)
	if request.method == 'POST':
		user.delete()
		user_trail(request.user.name, 'deleted customer: '+ str(user.name))
		return HttpResponse('success')

@permission_decorator('customer.change_customer')
def user_edit(request, pk):
	user = get_object_or_404(Customer, pk=pk)		
	ctx = {'user': user}
	user_trail(request.user.name, 'accessed edit page for customer '+ str(user.name),'update')
	info_logger.info('User: '+str(request.user.name)+' accessed edit page for customer: '+str(user.name))
	return TemplateResponse(request, 'dashboard/customer/edit_user.html', ctx)

def user_update(request, pk):
	user = get_object_or_404(Customer, pk=pk)
	if request.method == 'POST':
		name = request.POST.get('name')		
		email = request.POST.get('email')
		if request.POST.get('creditable'):
			user.creditable = True
		else:
			user.creditable = False
		nid = request.POST.get('nid')
		mobile = request.POST.get('mobile').replace(' ','').replace('(','').replace(')','').replace('-','')		
		user.name = name
		user.email = email			
		user.nid = nid
		user.mobile = mobile		
		user.save()
		user_trail(request.user.name, 'updated customer: '+ str(user.name))
		info_logger.info('User: '+str(request.user.name)+' updated customer: '+str(user.name))
		return HttpResponse("success")
		
@staff_member_required
def customer_pagination(request):
	page = int(request.GET.get('page', 1))
	list_sz = request.GET.get('size')
	p2_sz = request.GET.get('psize')
	select_sz = request.GET.get('select_size')

	users = Customer.objects.all().order_by('-id')
	if list_sz:
		paginator = Paginator(users, int(list_sz))
		users = paginator.page(page)
		return TemplateResponse(request, 'dashboard/customer/pagination/p2.html',
								{'users':users, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0})
	else:
		paginator = Paginator(users, 10)
	if p2_sz:
		paginator = Paginator(users, int(p2_sz))
		users = paginator.page(page)
		return TemplateResponse(request, 'dashboard/customer/pagination/paginate.html', {"users":users})

	try:
		users = paginator.page(page)
	except PageNotAnInteger:
		users = paginator.page(1)
	except InvalidPage:
		users = paginator.page(1)
	except EmptyPage:
		users = paginator.page(paginator.num_pages)
	return TemplateResponse(request, 'dashboard/customer/pagination/paginate.html', {"users":users})

@staff_member_required
def customer_search(request):
	if request.is_ajax():
		page = request.GET.get('page', 1)
		list_sz = request.GET.get('size', 10)
		p2_sz = request.GET.get('psize')
		q = request.GET.get('q')
		if list_sz == 0:
			sz = 10
		else:
			sz = list_sz

		if q is not None:
			queryset_list = Customer.objects.filter(
				Q(name__icontains=q)|
				Q(email__icontains=q) |
				Q(mobile__icontains=q)
			).order_by('-id')
			paginator = Paginator(queryset_list, 10)

			try:
				queryset_list = paginator.page(page)
			except PageNotAnInteger:
				queryset_list = paginator.page(1)
			except InvalidPage:
				queryset_list = paginator.page(1)
			except EmptyPage:
				queryset_list = paginator.page(paginator.num_pages)
			users = queryset_list
			if p2_sz:
				users = paginator.page(page)
				return TemplateResponse(request, 'dashboard/customer/pagination/paginate.html', {"users":users})

			return TemplateResponse(request, 'dashboard/customer/pagination/search.html',
			{"users":users, 'pn': paginator.num_pages, 'sz': sz, 'q': q})


@staff_member_required
def is_creditable(request):
    if request.method == "POST":
        if request.POST.get('pk'):        	 
            customer = Customer.objects.get(pk=int(request.POST.get("pk")))
            if request.POST.get('is_creditable'):
            	if int(request.POST.get('is_creditable')) == 1:
            		customer.creditable = True;
            	if int(request.POST.get('is_creditable')) == 0:
            		customer.creditable = False;
            	customer.save()
            return HttpResponse(json.dumps({'success':customer.creditable}),content_type='application/json')
    else:
        return HttpResponse(json.dumps({'error':'Invalid method GET'}),content_type='applicatoin/json')

# reports
@staff_member_required
@permission_decorator('customer.view_customer')
def customer_report(request):
	try:
		users = Customer.objects.all().order_by('-id')
		page = request.GET.get('page', 1)
		paginator = Paginator(users, 10)
		try:
			users = paginator.page(page)
		except PageNotAnInteger:
			users = paginator.page(1)
		except InvalidPage:
			users = paginator.page(1)
		except EmptyPage:
			users = paginator.page(paginator.num_pages)
		user_trail(request.user.name, 'accessed customers page', 'view')
		info_logger.info('User: ' + str(request.user.name) + 'view customers')
		if request.GET.get('initial'):
			return HttpResponse(paginator.num_pages)
		else:
			return TemplateResponse(request, 'dashboard/customer/reports/list.html',{'users': users, 'pn': paginator.num_pages})
	except TypeError as e:
		error_logger.error(e)
		return TemplateResponse(request, 'dashboard/customer/reports/list.html', {'users': users, 'pn': paginator.num_pages})

@staff_member_required
def report_search(request):
	if request.is_ajax():
		page = request.GET.get('page', 1)
		list_sz = request.GET.get('size', 10)
		p2_sz = request.GET.get('psize')
		q = request.GET.get('q')
		if list_sz == 0:
			sz = 10
		else:
			sz = list_sz

		if q is not None:
			queryset_list = Customer.objects.filter(
				Q(name__icontains=q)|
				Q(email__icontains=q) |
				Q(mobile__icontains=q)
			).order_by('-id')
			paginator = Paginator(queryset_list, 10)

			try:
				queryset_list = paginator.page(page)
			except PageNotAnInteger:
				queryset_list = paginator.page(1)
			except InvalidPage:
				queryset_list = paginator.page(1)
			except EmptyPage:
				queryset_list = paginator.page(paginator.num_pages)
			users = queryset_list
			if p2_sz:
				users = paginator.page(page)
				return TemplateResponse(request, 'dashboard/customer/pagination/report_paginate.html', {"users":users})

			return TemplateResponse(request, 'dashboard/customer/pagination/report_search.html',
			{"users":users, 'pn': paginator.num_pages, 'sz': sz, 'q': q})

@staff_member_required
def report_pagination(request):
	page = int(request.GET.get('page', 1))
	list_sz = request.GET.get('size')
	p2_sz = request.GET.get('psize')
	select_sz = request.GET.get('select_size')

	users = Customer.objects.all().order_by('-id')
	if list_sz:
		paginator = Paginator(users, int(list_sz))
		users = paginator.page(page)
		return TemplateResponse(request, 'dashboard/customer/pagination/report_p2.html',
								{'users':users, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0})
	else:
		paginator = Paginator(users, 10)
	if p2_sz:
		paginator = Paginator(users, int(p2_sz))
		users = paginator.page(page)
		return TemplateResponse(request, 'dashboard/customer/pagination/report_paginate.html', {"users":users})

	try:
		users = paginator.page(page)
	except PageNotAnInteger:
		users = paginator.page(1)
	except InvalidPage:
		users = paginator.page(1)
	except EmptyPage:
		users = paginator.page(paginator.num_pages)
	return TemplateResponse(request, 'dashboard/customer/pagination/report_paginate.html', {"users":users})

# credit views
@staff_member_required
@permission_decorator('customer.view_customer')
def credit_report(request):
	try:
		users =  Credit.objects.filter(~Q(customer=None)).order_by('-id')
		page = request.GET.get('page', 1)
		paginator = Paginator(users, 10)
		try:
			users = paginator.page(page)
		except PageNotAnInteger:
			users = paginator.page(1)
		except InvalidPage:
			users = paginator.page(1)
		except EmptyPage:
			users = paginator.page(paginator.num_pages)
		user_trail(request.user.name, 'accessed customers page', 'view')
		info_logger.info('User: ' + str(request.user.name) + 'view customers')
		if request.GET.get('initial'):
			return HttpResponse(paginator.num_pages)
		else:
			return TemplateResponse(request, 'dashboard/customer/credit/list.html',{'users': users, 'pn': paginator.num_pages})
	except TypeError as e:
		error_logger.error(e)
		return TemplateResponse(request, 'dashboard/customer/credit/list.html', {'users': users, 'pn': paginator.num_pages})

@staff_member_required
def credit_search(request):
	if request.is_ajax():
		page = request.GET.get('page', 1)
		list_sz = request.GET.get('size', 10)
		p2_sz = request.GET.get('psize')
		q = request.GET.get('q')
		if list_sz == 0:
			sz = 10
		else:
			sz = list_sz
		if q is not None:
			queryset_list = Credit.objects.filter(~Q(customer=None)).filter(
				Q(customer__name__icontains=q)|
				Q(customer__email__icontains=q) |
				Q(customer__mobile__icontains=q)
			).order_by('-id')
			paginator = Paginator(queryset_list, 10)

			try:
				queryset_list = paginator.page(page)
			except PageNotAnInteger:
				queryset_list = paginator.page(1)
			except InvalidPage:
				queryset_list = paginator.page(1)
			except EmptyPage:
				queryset_list = paginator.page(paginator.num_pages)
			users = queryset_list
			if p2_sz:
				users = paginator.page(page)
				return TemplateResponse(request, 'dashboard/customer/pagination/credit_paginate.html', {"users":users})

			return TemplateResponse(request, 'dashboard/customer/pagination/credit_search.html',
			{"users":users, 'pn': paginator.num_pages, 'sz': sz, 'q': q})

@staff_member_required
def credit_pagination(request):
	page = int(request.GET.get('page', 1))
	list_sz = request.GET.get('size')
	p2_sz = request.GET.get('psize')
	select_sz = request.GET.get('select_size')

	users = Credit.objects.filter(~Q(customer=None)).order_by('-id')
	if list_sz:
		paginator = Paginator(users, int(list_sz))
		users = paginator.page(page)
		return TemplateResponse(request, 'dashboard/customer/pagination/credit_p2.html',
								{'users':users, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0})
	else:
		paginator = Paginator(users, 10)
	if p2_sz:
		paginator = Paginator(users, int(p2_sz))
		users = paginator.page(page)
		return TemplateResponse(request, 'dashboard/customer/pagination/credit_paginate.html', {"users":users})

	try:
		users = paginator.page(page)
	except PageNotAnInteger:
		users = paginator.page(1)
	except InvalidPage:
		users = paginator.page(1)
	except EmptyPage:
		users = paginator.page(paginator.num_pages)
	return TemplateResponse(request, 'dashboard/customer/pagination/credit_paginate.html', {"users":users})

