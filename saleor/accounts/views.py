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
from ..site.models import Bank, BankBranch, UserRole, Department
from .models import ExpenseType, Expenses
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


def expenses(request):
    staff = Staff.objects.all()
    data = {
        "users":staff
    }
    user_trail(request.user.name, 'accessed employees', 'views')
    info_logger.info('User: ' + str(request.user.name) + 'accessed employee page')
    return TemplateResponse(request, 'dashboard/accounts/expenses/list.html',data)

def detail(request):
    status = 'read'
    return TemplateResponse(request, 'dashboard/accounts/expenses/expenses.html', {})

def add(request):
    expense_types =ExpenseType.objects.all()
    staff = Staff.objects.all()
    data = {
        "expense_types":expense_types,
        "staff":staff
    }
    user_trail(request.user.name, 'viewed add expenses page', 'view')
    info_logger.info('User: ' + str(request.user.name) + 'viewed add expenses page')
    return TemplateResponse(request, 'dashboard/accounts/expenses/expenses.html', data)

def add_process(request):
    voucher = request.POST.get('voucher')
    expense_type = request.POST.get('expense_type')
    expense_date = request.POST.get('expense_date')
    amount = request.POST.get('amount')
    authorized_by = request.POST.get('authorized_by')
    paid_to  = request.POST.get('paid_to')
    received_by = request.POST.get('received_by')
    phone = request.POST.get('phone')
    payment_mode = request.POST.get('payment_mode')
    description = request.POST.get('description')
    new_expense = Expenses(voucher=voucher, expense_type=expense_type, expense_date=expense_date,
                        amount=amount, authorized_by=authorized_by, paid_to=paid_to,
                        received_by=received_by, phone=phone, payment_mode=payment_mode,
                        description=description)
    try:
        new_expense.save()
        user_trail(request.user.name, 'created expense type : ' + str(expense_type), 'add')
        info_logger.info('User: ' + str(request.user.name) + 'created expense type:' + str(expense_type))
        return HttpResponse('success')
    except Exception as e:
        error_logger.info('Error when saving ')
        error_logger.error('Error when saving ')
        return HttpResponse(e)

def edit(request, pk=None):
    return TemplateResponse(request, 'dashboard/accounts/expenses/edit_expense.html', {})

def delete(request, pk=None):
    return TemplateResponse(request, 'dashboard/accounts/expenses/delete_expense.html', {})