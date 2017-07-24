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
# @permission_decorator('userprofile.view_user')
def view_bank(request):
	try:
		banks = Bank.objects.all().order_by('-id')
		page = request.GET.get('page', 1)
		paginator = Paginator(banks, 10)
		try:
			banks = paginator.page(page)
		except PageNotAnInteger:
			banks = paginator.page(1)
		except InvalidPage:
			banks = paginator.page(1)
		except EmptyPage:
			banks = paginator.page(paginator.num_pages)
		user_trail(request.user.name, 'accessed the banks page','view')
		info_logger.info('User: '+str(request.user.name)+' accessed the banks page page')
		if request.GET.get('initial'):
			return HttpResponse(paginator.num_pages)
		else:
			return TemplateResponse(request, 'dashboard/sites/hr/bank/view.html', {'banks':banks, 'totalp':paginator.num_pages})
	except TypeError as e:
		error_logger.error(e)
		return HttpResponse('error accessing users')

@staff_member_required
def bank_paginate(request):
	page = int(request.GET.get('page', 1))
	list_sz = request.GET.get('size')
	p2_sz = request.GET.get('psize')
	select_sz = request.GET.get('select_size')

	try:
		banks = Bank.objects.all().order_by('-id')
		if list_sz:
			paginator = Paginator(banks, int(list_sz))
			banks = paginator.page(page)
			data = {
				'banks': banks,
				'pn': paginator.num_pages,
				'sz': list_sz,
				'gid': 0
			}
			return TemplateResponse(request, 'dashboard/sites/hr/bank/p2.html', data)
		else:
			paginator = Paginator(banks, 10)
			if p2_sz:
				paginator = Paginator(banks, int(p2_sz))
			banks = paginator.page(page)
			data = {
				"banks": banks
			}
			return TemplateResponse(request, 'dashboard/sites/hr/bank/paginate.html', data)

		try:
			banks = paginator.page(page)
		except PageNotAnInteger:
			banks = paginator.page(1)
		except InvalidPage:
			banks = paginator.page(1)
		except EmptyPage:
			banks = paginator.page(paginator.num_pages)
		return TemplateResponse(request, 'dashboard/sites/hr/bank/paginate.html', {"banks": banks})
	except Exception, e:
		return  HttpResponse()



@staff_member_required
def add_bank(request):
	bank = request.POST.get('bank')
	option = request.POST.get('option')
	new_bank = Bank(name=bank)

	if option:
		try:
			new_bank.save()
			banks = Bank.objects.all()
			data = {"banks": banks}
			return TemplateResponse(request, 'dashboard/sites/hr/select_role.html', data)
		except IntegrityError as e:
			error_logger.error(e)
			return HttpResponse('error')
		except ValidationError as e:
			error_logger.error(e)
			return HttpResponse('error')
	else:
		try:
			new_bank.save()
			banks = Bank.objects.all()
			data = {"banks": banks}
			return TemplateResponse(request, 'dashboard/sites/hr/bank.html', data)
		except IntegrityError as e:
			error_logger.error(e)
			return HttpResponse('error')
		except ValidationError as e:
			error_logger.error(e)
			return HttpResponse('error')

def bank_delete(request, pk):
	bank = get_object_or_404(Bank, pk=pk)
	if request.method == 'POST':
		bank.delete()
		user_trail(request.user.name, 'deleted bank role: '+ str(bank.name),'delete')
		return HttpResponse('success')

def bank_edit(request, pk):
	bank = get_object_or_404(Bank, pk=pk)
	if request.method == 'POST':
		new_bank = request.POST.get('bank')
		bank.name = new_bank
		bank.save()
		user_trail(request.user.name, 'updated bank from: '+ str(bank.name) + ' to: '+str(new_bank),'update')
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
            banks = Bank.objects.filter(
                Q(name__icontains=q)).order_by('-id')
            paginator = Paginator(banks, 10)
            try:
                banks = paginator.page(page)
            except PageNotAnInteger:
                banks = paginator.page(1)
            except InvalidPage:
                banks = paginator.page(1)
            except EmptyPage:
                banks = paginator.page(paginator.num_pages)
            if p2_sz:
                banks = paginator.page(page)
                return TemplateResponse(request, 'dashboard/sites/hr/bank/paginate.html', {'banks': banks})

            return TemplateResponse(request, 'dashboard/sites/hr/bank/search.html',
                                    {'banks': banks, 'pn': paginator.num_pages, 'sz': sz, 'q': q})