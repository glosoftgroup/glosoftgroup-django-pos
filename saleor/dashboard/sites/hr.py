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

def add_role(request):
	role = request.POST.get('user_role')
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
			user_roles = UserRole.objects.all()
			data = {"user_roles": user_roles}
			return TemplateResponse(request, 'dashboard/sites/hr/roles.html', data)
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