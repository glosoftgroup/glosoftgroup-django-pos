
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
from .models import PettyCash

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

def view(request):
	try:
		try:
			petty_cash = get_object_or_404(PettyCash, pk=1)
			amount = petty_cash.amount
		except:
			amount = 0
		data = { "amount": amount }
		return TemplateResponse(request, 'dashboard/accounts/petty_cash/view.html', data)
	except Exception, e:
		return HttpResponse(e)

def add(request):
	amount = request.POST.get('amount')
	petty_cash = get_object_or_404(PettyCash, pk=1)
	petty_cash_amount = petty_cash.amount
	try:
		petty_cash_amount += Decimal(amount)
		petty_cash.amount = petty_cash_amount
		petty_cash.save()
		current_amount = get_object_or_404(PettyCash, pk=1)
		user_trail(request.user.name, 'petty cash balance: '+ str(petty_cash.amount)+' added '+ str(amount)+' balance '+ str(petty_cash_amount)+', total', 'update')
		info_logger.info('User: ' + str(request.user.name) + 'accessed expenses page')
		return HttpResponse(current_amount.amount)
	except Exception, e:
		return HttpResponse(e)

def balance(request):
	try:
		current_amount = get_object_or_404(PettyCash, pk=1)
		return HttpResponse(current_amount.amount)
	except Exception, e:
		return HttpResponse(e)