from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.http import is_safe_url
from django.utils.translation import pgettext_lazy
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.db.models import Q
from django.db import IntegrityError
import json
import simplejson
from ...core.utils import get_paginator_items
from ..views import staff_member_required
from ...site.models import Bank, BankBranch, UserRole, Department
from ...decorators import permission_decorator, user_trail
from django.core.paginator import Paginator

import logging

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
def view_department(request):
	try:
		departments = Department.objects.all().order_by('-id')
		page = request.GET.get('page', 1)
		paginator = Paginator(departments, 10)
		try:
			departments = paginator.page(page)
		except PageNotAnInteger:
			departments = paginator.page(1)
		except InvalidPage:
			departments = paginator.page(1)
		except EmptyPage:
			departments = paginator.page(paginator.num_pages)
		user_trail(request.user.name, 'accessed the departments page','view')
		info_logger.info('User: '+str(request.user.name)+' accessed the departments page page')
		if request.GET.get('initial'):
			return HttpResponse(paginator.num_pages)
		else:
			return TemplateResponse(request, 'dashboard/sites/hr/department/view.html', {'departments':departments, 'totalp':paginator.num_pages})
	except TypeError as e:
		error_logger.error(e)
		return HttpResponse('error accessing users')

@staff_member_required
def department_paginate(request):
	page = int(request.GET.get('page', 1))
	list_sz = request.GET.get('size')
	p2_sz = request.GET.get('psize')
	select_sz = request.GET.get('select_size')

	try:
		departments = Department.objects.all().order_by('-id')
		if list_sz:
			paginator = Paginator(departments, int(list_sz))
			departments = paginator.page(page)
			data = {
				'departments': departments,
				'pn': paginator.num_pages,
				'sz': list_sz,
				'gid': 0
			}
			return TemplateResponse(request, 'dashboard/sites/hr/department/p2.html', data)
		else:
			paginator = Paginator(departments, 10)
			if p2_sz:
				paginator = Paginator(departments, int(p2_sz))
			departments = paginator.page(page)
			data = {
				"departments": departments
			}
			return TemplateResponse(request, 'dashboard/sites/hr/department/paginate.html', data)

		try:
			departments = paginator.page(page)
		except PageNotAnInteger:
			departments = paginator.page(1)
		except InvalidPage:
			departments = paginator.page(1)
		except EmptyPage:
			departments = paginator.page(paginator.num_pages)
		return TemplateResponse(request, 'dashboard/sites/hr/department/paginate.html', {"departments": departments})
	except Exception, e:
		return  HttpResponse()

@staff_member_required
def add_department(request):
	department = request.POST.get('department')
	option = request.POST.get('option')
	new_department = Department(name=department)
	if option:
		try:
			new_department.save()
			departments = Department.objects.all()
			data = {"departments": departments}
			return TemplateResponse(request, 'dashboard/sites/hr/select_role.html', data)
		except IntegrityError as e:
			error_logger.error(e)
			return HttpResponse('error')
		except ValidationError as e:
			error_logger.error(e)
			return HttpResponse('error')
	else:
		try:
			new_department.save()
			departments =Department.objects.all()
			data = {"departments": departments}
			return TemplateResponse(request, 'dashboard/sites/hr/department.html', data)
		except IntegrityError as e:
			error_logger.error(e)
			return HttpResponse('error')
		except ValidationError as e:
			error_logger.error(e)
			return HttpResponse('error')

def department_delete(request, pk):
	department = get_object_or_404(Department, pk=pk)
	if request.method == 'POST':
		department.delete()
		user_trail(request.user.name, 'deleted department: '+ str(department.name),'delete')
		return HttpResponse('success')

def department_edit(request, pk):
	department = get_object_or_404(Department, pk=pk)
	if request.method == 'POST':
		new_department = request.POST.get('department')
		department.name = new_department
		department.save()
		user_trail(request.user.name, 'updated user role from: '+ str(department.name) + ' to: '+str(new_department),'update')
		return HttpResponse('success')

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
            departments = Department.objects.filter(
                Q(name__icontains=q)).order_by('-id')
            paginator = Paginator(departments, 10)
            try:
                departments = paginator.page(page)
            except PageNotAnInteger:
                departments = paginator.page(1)
            except InvalidPage:
                departments = paginator.page(1)
            except EmptyPage:
                departments = paginator.page(paginator.num_pages)
            if p2_sz:
                departments = paginator.page(page)
                return TemplateResponse(request, 'dashboard/sites/hr/department/paginate.html', {'departments': departments})

            return TemplateResponse(request, 'dashboard/sites/hr/department/search.html',
                                    {'departments':departments, 'pn': paginator.num_pages, 'sz': sz, 'q': q})