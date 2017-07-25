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
def view(request, pk=None):
	try:
		bank = Bank.objects.get(pk=pk)
		branches = BankBranch.objects.filter(bank=pk).order_by('-id')
		page = request.GET.get('page', 1)
		paginator = Paginator(branches, 10)
		try:
			branches = paginator.page(page)
		except PageNotAnInteger:
			branches = paginator.page(1)
		except InvalidPage:
			branches = paginator.page(1)
		except EmptyPage:
			branches = paginator.page(paginator.num_pages)
		user_trail(request.user.name, 'accessed the branches page for bank: '+bank.name,'view')
		info_logger.info('User: '+str(request.user.name)+'accessed the branches page for bank: '+bank.name,'view')
		if request.GET.get('initial'):
			return HttpResponse(paginator.num_pages)
		else:
			return TemplateResponse(request, 'dashboard/sites/hr/bank/branch/view.html', {'branches':branches, 'bank':bank,'totalp':paginator.num_pages})
	except TypeError as e:
		error_logger.error(e)
		return HttpResponse('error accessing users')


@staff_member_required
def branch_paginate(request):
	page = int(request.GET.get('page', 1))
	list_sz = request.GET.get('size')
	p2_sz = request.GET.get('psize')
	select_sz = request.GET.get('select_size')
	bank_pk = request.GET.get('bank_pk')

	try:
		bank = Bank.objects.get(pk=bank_pk)
		branches = BankBranch.objects.filter(bank__pk=bank_pk).order_by('-id')
		if list_sz:
			paginator = Paginator(branches, int(list_sz))
			branches = paginator.page(page)
			data = {
				'branches': branches,
				'pn': paginator.num_pages,
				'sz': list_sz,
				'gid': 0,
				'bank': bank
			}
			return TemplateResponse(request, 'dashboard/sites/hr/bank/branch/p2.html', data)
		else:
			paginator = Paginator(branches, 10)
			if p2_sz:
				paginator = Paginator(branches, int(p2_sz))
			branches = paginator.page(page)
			data = {
				"branches": branches,
				'bank': bank
			}
			return TemplateResponse(request, 'dashboard/sites/hr/bank/branch/paginate.html', data)

		try:
			branches = paginator.page(page)
		except PageNotAnInteger:
			branches = paginator.page(1)
		except InvalidPage:
			branches = paginator.page(1)
		except EmptyPage:
			branches = paginator.page(paginator.num_pages)
		return TemplateResponse(request, 'dashboard/sites/hr/bank/branch/paginate.html', {"branches": branches})

	except Exception, e:
		return  HttpResponse(e)

@staff_member_required
def add_branch(request):
	branch = request.POST.get('branch')
	option = request.POST.get('option')
	bank_pk = request.POST.get('bank_pk')
	bank = Bank.objects.get(pk=bank_pk)
	new_branch = BankBranch(name=branch, bank=bank)

	if option:
		try:
			new_branch.save()
			branches = BankBranch.objects.all()
			data = {"branches": branches}
			return TemplateResponse(request, 'dashboard/sites/hr/select_role.html', data)
		except IntegrityError as e:
			error_logger.error(e)
			return HttpResponse('error')
		except ValidationError as e:
			error_logger.error(e)
			return HttpResponse('error')
	else:
		try:
			new_branch.save()
			branches = BankBranch.objects.all()
			data = {"branches": branches}
			return TemplateResponse(request, 'dashboard/sites/hr/branch.html', data)
		except IntegrityError as e:
			error_logger.error(e)
			return HttpResponse('error')
		except ValidationError as e:
			error_logger.error(e)
			return HttpResponse('error')

def branch_delete(request, pk):
	branch = get_object_or_404(BankBranch, pk=pk)
	if request.method == 'POST':
		branch.delete()
		user_trail(request.user.name, 'deleted branch role: '+ str(branch.name),'delete')
		return HttpResponse('success')

def branch_edit(request, pk):
	branch = get_object_or_404(BankBranch, pk=pk)
	if request.method == 'POST':
		new_branch = request.POST.get('branch')
		branch.name = new_branch
		branch.save()
		user_trail(request.user.name, 'updated branch from: '+ str(branch.name) + ' to: '+str(new_branch),'update')
		return HttpResponse('success')

def search(request):
	if request.is_ajax():
		page = request.GET.get('page', 1)
		list_sz = request.GET.get('size', 10)
		p2_sz = request.GET.get('psize')
		q = request.GET.get('q')
		bank_pk = request.GET.get('bank_pk')
		if list_sz is None:
			sz = 10
		else:
			sz = list_sz

	if q is not None:
 		bank = BankBranch.objects.filter(bank__pk=bank_pk)
		# branches = bank.filter(
		# 	Q(name__icontains=q)).order_by('-id')
		branches = BankBranch.objects.filter(Q(name__icontains=q)).order_by('-id').filter(bank__pk=bank_pk)
		paginator = Paginator(branches, 10)
		try:
			branches = paginator.page(page)
		except PageNotAnInteger:
			branches = paginator.page(1)
		except InvalidPage:
			branches = paginator.page(1)
		except EmptyPage:
			branches = paginator.page(paginator.num_pages)
		if p2_sz:
			branches = paginator.page(page)
			return TemplateResponse(request, 'dashboard/sites/hr/bank/branch/paginate.html', {'branches': branches, 'bank':bank})

		return TemplateResponse(request, 'dashboard/sites/hr/bank/branch/search.html',
		{'branches': branches, 'bank':bank, 'pn': paginator.num_pages, 'sz': sz, 'q': q})