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

from ...core.utils import get_paginator_items
from ..views import staff_member_required
from ...userprofile.models import User, Staff, Attendance
from ...supplier.models import Supplier
from ...customer.models import Customer
from ...sale.models import Sales, SoldItem, Terminal
from ...product.models import Product, ProductVariant, Category
from ...decorators import permission_decorator, user_trail
from ...utils import render_to_pdf, convert_html_to_pdf
from ...site.models import UserRole, Department, BankBranch, Bank

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


def attendance(request):
	staff = Staff.objects.all()
	data = {
		"users":staff
	}
	user_trail(request.user.name, 'accessed attendance', 'view')
	info_logger.info('User: ' + str(request.user.name) + ' acccess attenndance')
	return TemplateResponse(request, 'dashboard/hr/attendance/list.html',data)

def detail(request):
    status = 'read'
    return TemplateResponse(request, 'dashboard/hr/attendance/employee.html', {})

def add(request):
	departments = Department.objects.all()
	roles = UserRole.objects.all()
	banks = Bank.objects.all()
	branches = BankBranch.objects.all()
	data = {
		"roles":roles,
		"departments":departments,
		"banks":banks,
		"branches":branches
	}
	user_trail(request.user.name, 'accessed attendance filling page', 'view')
	info_logger.info('User: ' + str(request.user.name) + 'accessed attendance filling page')
	return TemplateResponse(request, 'dashboard/hr/attendance/fill_attendance.html', data)

def add_process(request):
    name = request.POST.get('name')
    time_in = request.POST.get('time_in')
    time_out = request.POST.get('time_out')
    department = request.POST.get('department')
    date = request.POST.get('date')
    new_attendance = Attendance( name=name, time_in=time_in,
                      time_out=time_out, date=date, department=department)
    try:
		new_attendance.save()
		user_trail(request.user.name, 'filled in attendance', 'add')
		info_logger.info('User: ' + str(request.user.name) + 'filled in attendance')
		return HttpResponse('success')
    except Exception as e:
        error_logger.info('Error when saving ')
        error_logger.error('Error when saving ')
        return HttpResponse(e)