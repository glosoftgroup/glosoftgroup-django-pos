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
import datetime
from datetime import date, timedelta
from django.utils.dateformat import DateFormat
import logging

from ...core.utils import get_paginator_items
from ..views import staff_member_required
from ...userprofile.models import User
from ...sale.models import Sales, SoldItem
from ...product.models import Product, ProductVariant
from ...decorators import permission_decorator, user_trail

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
def sales_date_chart(request):
	return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_date.html', {})

def get_sales_charts(request):
	label = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]
	default = [12, 19, 3, 5, 2, 3]
	total_sales = Sales.objects.all()
	today = datetime.date.today()
	todays_sales = Sales.objects.filter(created=today).annotate(Sum('total_net'))

	data = {
		 "label":label,
		 "default":default,
		 "users":10,
		 "net":serializers.serialize('json', total_sales),
		 "todays_sales": serializers.serialize('json', todays_sales),
	}
	return JsonResponse(data)
def get_sales_by_date(request):
	date = request.GET.get('date')
	# if date:
	items = SoldItem.objects.filter(sales__created__icontains=date)
	item_occurences = items.values('product_name','total_cost').annotate(c=Count('sku')).order_by('-c')
	
	highest_no = item_occurences.aggregate(Max('c'))['c__max']
	highest_product = item_occurences.get(c=highest_no)

	lowest_no = item_occurences.aggregate(Min('c'))['c__min']
	lowest_product = item_occurences.filter(c=lowest_no)

	data = {
		"highest_product": highest_product,
		"lowest_product":list(lowest_product)
	}
	return JsonResponse(data)

def sales_user_chart(request):
	return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_user.html', {})

def sales_product_chart(request):
	return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_product.html', {})

def sales_teller_chart(request):
	return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_teller.html', {})