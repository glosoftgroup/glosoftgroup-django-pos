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

from ...core.utils import get_paginator_items
from ..views import staff_member_required
from ...userprofile.models import User
from ...sale.models import Sales, SoldItem
from ...product.models import Product, ProductVariant
from ...decorators import permission_decorator, user_trail

from .hours_chart import get_hours_results

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
	if date:
		try:
			no_of_customers = Sales.objects.filter(created__contains=date).count()
			date_total_sales = Sales.objects.filter(created__contains=date).aggregate(Sum('total_net'))['total_net__sum']
			items = SoldItem.objects.filter(sales__created__icontains=date)
			# to get all items and their totals
			item_occurences = items.values('product_name','total_cost').annotate(c=Count('sku')).annotate(Sum('total_cost'))
			popular_no = item_occurences.aggregate(Max('c'))['c__max']
			popular_item = item_occurences.filter(c=popular_no)

			highest_sale = item_occurences.aggregate(Max('total_cost__sum'))['total_cost__sum__max']
			highest_item = item_occurences.get(total_cost__sum=highest_sale)

			# lowest_no = item_occurences.aggregate(Min('c'))['c__min']
			# lowest_product = item_occurences.filter(c=lowest_no)
			lowest_sale = item_occurences.aggregate(Min('total_cost__sum'))['total_cost__sum__min']
			lowest_item = item_occurences.get(total_cost__sum=lowest_sale)

			seven_eight = get_hours_results(date, 7, 8)
			eight_nine = get_hours_results(date, 8, 9)
			nine_ten = get_hours_results(date, 9, 10)
			ten_eleven = get_hours_results(date, 10, 11)
			eleven_twelve = get_hours_results(date, 11, 12)
			twelve_thirteen = get_hours_results(date, 12, 13)
			thriteen_fourteen = get_hours_results(date, 13, 14)
			fourteen_fifteen = get_hours_results(date, 14, 15)
			fifteen_sixteen = get_hours_results(date, 15, 16)
			sixteen_seventeen = get_hours_results(date, 16, 17)
			seventeen_eighteen = get_hours_results(date, 17, 18)
			eighteen_nineteen = get_hours_results(date, 18, 19)
			nineteen_twenty = get_hours_results(date, 19, 20)
			twenty_twentyone = get_hours_results(date, 20, 21)

			labels = ["7-8","8-9", "9-10", "10-11", "11-12", "12-13", "13-14",
			"14-15","15-16","16-17","17-18","18-19","19-20","20-21"]
			default = [seven_eight, eight_nine, nine_ten, ten_eleven, 
			eleven_twelve, twelve_thirteen, thriteen_fourteen, fourteen_fifteen, 
			fifteen_sixteen, sixteen_seventeen, seventeen_eighteen, 
			eighteen_nineteen, nineteen_twenty,twenty_twentyone]

			data = {
				"highest_item": highest_item,
				"lowest_item":lowest_item,
				"no_of_customers":no_of_customers,
				"date_total_sales":date_total_sales,
				"popular_item":popular_item,
				"date":date,
				"labels":labels,
				"default":default
			}
			return TemplateResponse(request, 'dashboard/reports/sales/charts/by_date.html',data)
		except ObjectDoesNotExist as e:
			return TemplateResponse(request, 'dashboard/reports/sales/charts/by_date.html',{"error":e, "date":date})

def sales_user_chart(request):
	return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_user.html', {})

def sales_product_chart(request):
	return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_product.html', {})

def sales_teller_chart(request):
	return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_teller.html', {})