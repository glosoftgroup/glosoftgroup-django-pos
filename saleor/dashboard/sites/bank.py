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
def add_bank(request):
	bank = request.POST.get('bank')
	new_bank = Bank(name=bank)
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