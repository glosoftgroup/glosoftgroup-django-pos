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
from ...userprofile.models import User, Staff
from ...supplier.models import Supplier
from ...customer.models import Customer
from ...sale.models import Sales, SoldItem, Terminal
from ...product.models import Product, ProductVariant, Category
from ...decorators import permission_decorator, user_trail
from ...utils import render_to_pdf, convert_html_to_pdf
from ...site.models import UserRole, Department, BankBranch, Bank

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
@permission_decorator('userprofile.view_staff')
def employees(request):
	try:
		users = Staff.objects.all().order_by('-id')
		groups = UserRole.objects.all()
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
		user_trail(request.user.name, 'accessed employees', 'views')
		info_logger.info('User: '+str(request.user.name)+' accessed the employee page')
		if request.GET.get('initial'):
			return HttpResponse(paginator.num_pages)
		else:
			return TemplateResponse(request, 'dashboard/hr/employee/list.html', {'groups':groups,'users':users})
	except TypeError as e:
		error_logger.error(e)
		return HttpResponse('error accessing users')

def detail(request):
    status = 'read'
    return TemplateResponse(request, 'dashboard/hr/employee/employee.html', {})

def add(request):
    try:
        departments = Department.objects.all()
        roles = UserRole.objects.all()
        banks = Bank.objects.all()
        branches = BankBranch.objects.all()
        data = {
            "roles":roles,
            "departments":departments,
            "banks":banks,
            "branches":branches
        }
        user_trail(request.user.name, 'accessed add employee page', 'view')
        info_logger.info('User: ' + str(request.user.name) + 'viewed add employee page')
        return TemplateResponse(request, 'dashboard/hr/employee/add_employee.html', data)
    except Exception, e:
        error_logger.error(e)
        return HttpResponse(e)

def add_process(request):
    name = request.POST.get('name')
    gender = request.POST.get('gender')
    dob = request.POST.get('dob')
    email = request.POST.get('email')
    nid = request.POST.get('nid')
    doj = request.POST.get('doj')
    mobile = request.POST.get('phone')
    work_time = request.POST.get('work_time')
    role = request.POST.get('role')
    department = request.POST.get('department')
    account = request.POST.get('account')
    bank = request.POST.get('bank')
    branch = request.POST.get('branch')
    krapin = request.POST.get('krapin')
    nhif = request.POST.get('nhif')
    nssf = request.POST.get('nssf')
    location = request.POST.get('location')
    religion = request.POST.get('religion')
    marital_status = request.POST.get('marital_status')
    image = request.FILES.get('image')
    if image:
        new_staff = Staff( name=name, email=email, gender=gender,
                      dob=dob, date_joined=doj, mobile=mobile,
                      national_id=nid, work_time=work_time, role=role,
                      department=department, image=image, account=account,
                      bank_name=bank, bank_branch=branch, pin=krapin,
                      nssf=nssf, nhif=nhif, location=location,
                      religion=religion, marital_status=marital_status)
    else:
        new_staff = Staff(name=name, email=email, gender=gender,
                         dob=dob, date_joined=doj, mobile=mobile,
                         national_id=nid, work_time=work_time, role=role,
                         department=department, account=account,
                         bank_name=bank, bank_branch=branch, pin=krapin,
                         nssf=nssf, nhif=nhif, location=location,
                         religion=religion, marital_status=marital_status)
    try:
        new_staff.save()
        user_trail(request.user.name, 'created employee : ' + str(name), 'add')
        info_logger.info('User: ' + str(request.user.name) + 'created employee:' + str(ame))
        return HttpResponse('success')
    except Exception as e:
        error_logger.info('Error when saving ')
        error_logger.error('Error when saving ')
        return HttpResponse(e)

def edit(request, pk=None):
    return TemplateResponse(request, 'dashboard/hr/employee/edit_employee.html', {})

@staff_member_required
@permission_decorator('userprofile.delete_staff')
def delete(request, pk=None):
	user = get_object_or_404(Staff, pk=pk)
	if request.method == 'POST':
		user.delete()
		user_trail(request.user.name, 'deleted employee: '+ str(user.name),'delete')
        info_logger.info(request.user.name, 'deleted employee: '+ str(user.name),'delete')
        return HttpResponse('success')


@staff_member_required
def paginate(request):
	page = int(request.GET.get('page', 1))
	list_sz = request.GET.get('size')
	p2_sz = request.GET.get('psize')
	select_sz = request.GET.get('select_size')
	if request.GET.get('gid'):
		users = Staff.objects.filter(role=request.GET.get('gid'))
		if p2_sz:
			paginator = Paginator(users, int(p2_sz))
			users = paginator.page(page)
			return TemplateResponse(request,'dashboard/hr/employee/paginate.html',{'users':users})

		paginator = Paginator(users, 10)
		users = paginator.page(page)
		return TemplateResponse(request,'dashboard/hr/employee/p2.html',{'users':users, 'pn':paginator.num_pages,'sz':10,'gid':request.GET.get('gid')})

	else:
		users = Staff.objects.all().order_by('-id')
		if list_sz:
			paginator = Paginator(users, int(list_sz))
			users = paginator.page(page)
			return TemplateResponse(request,'dashboard/hr/employee/p2.html',{'users':users, 'pn':paginator.num_pages,'sz':list_sz, 'gid':0})
		else:
			paginator = Paginator(users, 10)
		if p2_sz:
			paginator = Paginator(users, int(p2_sz))
			users = paginator.page(page)
			return TemplateResponse(request,'dashboard/hr/employee/paginate.html',{'users':users})

		try:
			users = paginator.page(page)
		except PageNotAnInteger:
			users = paginator.page(1)
		except InvalidPage:
			groups = paginator.page(1)
		except EmptyPage:
			users = paginator.page(paginator.num_pages)
		return TemplateResponse(request,'dashboard/hr/employee/paginate.html',{'users':users})

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
            users = Staff.objects.filter(
                Q(name__icontains=q) |
                Q(email__icontains=q) | Q(mobile__icontains=q) |
                Q(role__icontains=q) | Q(department__icontains=q) |
                Q(national_id__icontains=q)).order_by('-id')
            paginator = Paginator(users, 10)
            try:
                users = paginator.page(page)
            except PageNotAnInteger:
                users = paginator.page(1)
            except InvalidPage:
                users = paginator.page(1)
            except EmptyPage:
                users = paginator.page(paginator.num_pages)
            if p2_sz:
                users = paginator.page(page)
                return TemplateResponse(request, 'dashboard/hr/employee/paginate.html', {'users': users})

            return TemplateResponse(request, 'dashboard/hr/employee/search.html',
                                    {'users': users, 'pn': paginator.num_pages, 'sz': sz, 'q': q})