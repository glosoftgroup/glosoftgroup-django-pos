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

from ..core.utils import get_paginator_items
from ..dashboard.views import staff_member_required
from ..userprofile.models import User, Staff
from ..supplier.models import Supplier
from ..customer.models import Customer
from ..sale.models import Sales, SoldItem, Terminal
from ..product.models import Product, ProductVariant, Category
from ..decorators import permission_decorator, user_trail
from ..utils import render_to_pdf, convert_html_to_pdf
from ..site.models import UserRole, Department, BankBranch, Bank
from .models import PettyCash, Expenses

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

def view(request):
	try:
		try:
			petty_cash = PettyCash.objects.latest('id')
			amount = petty_cash.balance
		except:
			amount = 0

		date = DateFormat(datetime.datetime.today()).format('Y-m-d')

		try:
			pettyCash = PettyCash.objects.filter(created__icontains=date)
			opening_amount = pettyCash.aggregate(Sum('opening_amount'))
			p = pettyCash.order_by('-id')[:1]
			balance = [i for i in p]
			expenses = Expenses.objects.filter(added_on__icontains=date)
			types = expenses.values('expense_type').annotate(Count('expense_type'))
			expense_amount = expenses.aggregate(Sum('amount'))['amount__sum']
		except:
			expenses = 0
			types = 0
			pettyCash = None
			opening_amount = 0
			expense_amount = 0
			balance = 0

		data = {
			'expenses': expenses,
			'types': types,
			'pettyCash': pettyCash,
			'opening_amount': opening_amount,
			'expense_amount': expense_amount,
			'balance': balance,

			'amount': amount
		}

		return TemplateResponse(request, 'dashboard/accounts/petty_cash/view.html', data)
	except Exception, e:
		return HttpResponse(e)

@staff_member_required
def add(request):
	amount = request.POST.get('amount')
	try:
		petty_cash = PettyCash.objects.latest('id')
		total = petty_cash.balance + Decimal(amount)
		print (petty_cash.balance)
		print (total)
		new_petty_cash = PettyCash(opening_amount=total, balance=total)
		previousBalance = petty_cash.balance
	except Exception, e:
		new_petty_cash = PettyCash(opening_amount=amount, balance=amount)
		previousBalance = 0
		print (e)

	try:
		new_petty_cash.save()
		user_trail(request.user.name, 'petty cash balance: '+ str(previousBalance)+', added '+ str(amount)+' current balance is '+ str(new_petty_cash.balance)+', total', 'update')
		info_logger.info('User: ' + str(request.user.name) + 'petty cash balance: '+ str(previousBalance)+', added '+ str(amount)+' current balance is '+ str(new_petty_cash.balance)+', total', 'update')
		return HttpResponse(new_petty_cash.balance)
	except Exception, e:
		print (e)
		return HttpResponse(e)

def balance(request):
	try:
		current_amount = PettyCash.objects.latest('id')
		amount = current_amount.balance
		return HttpResponse(amount)
	except Exception, e:
		amount = 0
		return HttpResponse(amount)

def expenditure(request):
	date = request.GET.get('date')
	try:
		pettyCash = PettyCash.objects.filter(created__icontains=date)
		opening_amount = pettyCash.aggregate(Sum('opening_amount'))
		p = pettyCash.order_by('-id')[:1]
		balance = [i for i in p]
		expenses = Expenses.objects.filter(added_on__icontains=date)
		types = expenses.values('expense_type').annotate(Count('expense_type'))
		amount = expenses.aggregate(Sum('amount'))['amount__sum']

		data = {
			'expenses':expenses,
			'types':types,
			'pettyCash':pettyCash,
			'opening_amount':opening_amount,
			'expense_amount':amount,
			'balance':balance
		}
		return TemplateResponse(request, 'dashboard/accounts/petty_cash/expenditure.html', data)
	except Exception, e:
		return HttpResponse(e)