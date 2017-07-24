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
def hr_defaults(request):
	try:
		user_roles = UserRole.objects.all()
		departments = Department.objects.all()
		banks = Bank.objects.all()
		branches = BankBranch.objects.all()
		data = {"user_roles":user_roles, "departments":departments, "banks":banks, "branches": branches}
		return TemplateResponse(request, 'dashboard/sites/hr/hr.html', data)
	except ObjectDoesNotExist as e:
		return HttpResponse(e)


@staff_member_required
def view_roles(request):
	try:
		roles = UserRole.objects.all().order_by('-id')
		page = request.GET.get('page', 1)
		paginator = Paginator(roles, 10)
		try:
			roles = paginator.page(page)
		except PageNotAnInteger:
			roles = paginator.page(1)
		except InvalidPage:
			roles = paginator.page(1)
		except EmptyPage:
			roles = paginator.page(paginator.num_pages)
		user_trail(request.user.name, 'accessed the roles page','view')
		info_logger.info('User: '+str(request.user.name)+' accessed the roles page page')
		if request.GET.get('initial'):
			return HttpResponse(paginator.num_pages)
		else:
			return TemplateResponse(request, 'dashboard/sites/hr/roles/view.html', {'roles':roles, 'totalp':paginator.num_pages})
	except TypeError as e:
		error_logger.error(e)
		return HttpResponse('error accessing users')

def roles_paginate(request):
	page = int(request.GET.get('page', 1))
	list_sz = request.GET.get('size')
	p2_sz = request.GET.get('psize')
	select_sz = request.GET.get('select_size')

	try:
		roles = UserRole.objects.all().order_by('-id')
		if list_sz:
			paginator = Paginator(roles, int(list_sz))
			roles = paginator.page(page)
			data = {
				'roles':roles,
				'pn': paginator.num_pages,
				'sz': list_sz,
				'gid': 0
			}
			return TemplateResponse(request, 'dashboard/sites/hr/roles/p2.html', data)
		else:
			paginator = Paginator(roles, 10)
			if p2_sz:
				paginator = Paginator(roles, int(p2_sz))
			roles = paginator.page(page)
			data = {
				"roles": roles
			}
			return TemplateResponse(request, 'dashboard/sites/hr/roles/paginate.html', data)

		try:
			roles = paginator.page(page)
		except PageNotAnInteger:
			roles = paginator.page(1)
		except InvalidPage:
			roles = paginator.page(1)
		except EmptyPage:
			roles = paginator.page(paginator.num_pages)
		return TemplateResponse(request, 'dashboard/sites/hr/roles/paginate.html', {"roles": roles})
	except Exception, e:
		return  HttpResponse()

def add_role(request):
	role = request.POST.get('role')
	option = request.POST.get('option')
	new_role = UserRole(name=role)

	if option:
		try:
			new_role.save()
			roles = UserRole.objects.all()
			data = {"roles": roles}
			return TemplateResponse(request, 'dashboard/sites/hr/select_role.html', data)
		except IntegrityError as e:
			error_logger.error(e)
			return HttpResponse('error')
		except ValidationError as e:
			error_logger.error(e)
			return HttpResponse('error')
	else:
		try:
			new_role.save()
			roles = UserRole.objects.all()
			data = {"roles": roles}
			return TemplateResponse(request, 'dashboard/sites/hr/roles/view.html', data)
		except IntegrityError as e:
			error_logger.error(e)
			return HttpResponse('error')
		except ValidationError as e:
			error_logger.error(e)
			return HttpResponse('error')

def role_delete(request, pk):
	role = get_object_or_404(UserRole, pk=pk)
	if request.method == 'POST':
		role.delete()
		user_trail(request.user.name, 'deleted user role: '+ str(role.name),'delete')
		return HttpResponse('success')

def role_edit(request, pk):
	role = get_object_or_404(UserRole, pk=pk)
	if request.method == 'POST':
		new_role = request.POST.get('user_role')
		role.name = new_role
		try:
			role.save()
			user_trail(request.user.name, 'updated user role from: '+ str(role.name) + ' to: '+str(new_role),'update')
			return HttpResponse('success')
		except:
			HttpResponse('error')
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
            roles = UserRole.objects.filter(
                Q(name__icontains=q)).order_by('-id')
            paginator = Paginator(roles, 10)
            try:
                roles = paginator.page(page)
            except PageNotAnInteger:
                roles = paginator.page(1)
            except InvalidPage:
                roles = paginator.page(1)
            except EmptyPage:
                roles = paginator.page(paginator.num_pages)
            if p2_sz:
                roles = paginator.page(page)
                return TemplateResponse(request, 'dashboard/sites/hr/roles/paginate.html', {'roles': roles})

            return TemplateResponse(request, 'dashboard/sites/hr/roles/search.html',
                                    {'roles':roles, 'pn': paginator.num_pages, 'sz': sz, 'q': q})