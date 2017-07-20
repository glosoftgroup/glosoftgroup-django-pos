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