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
from decimal import Decimal
from calendar import monthrange
from django_xhtml2pdf.utils import generate_pdf

from ...core.utils import get_paginator_items
from ..views import staff_member_required
from ...userprofile.models import User
from ...sale.models import Sales, SoldItem
from ...product.models import Product, ProductVariant
from ...decorators import permission_decorator, user_trail
from ...utils import render_to_pdf, convert_html_to_pdf

from .hours_chart import get_hours_results, get_hours_results_range, get_date_results_range, get_date_results

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
def sales_date_chart(request):
	return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_date.html', {})


def chart_pdf(request):
	users = User.objects.all()
	data = {
		'today': date.today(), 
		'users': users,
		'puller': request.user
		}
	pdf = render_to_pdf('dashboard/reports/sales/charts/pdf/pdf.html', data)
	return HttpResponse(pdf, content_type='application/pdf')

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
			td_sales = Sales.objects.filter(created__contains=date).order_by('-id')[:1]
			if td_sales:
				for dt in td_sales:
					seld = dt.created
				selected_sales_date = DateFormat(seld).format('jS F Y')
			else:
				selected_sales_date = date
			prev_sales = Sales.objects.filter(created__lte=date)[:1]
			if prev_sales:
				for dt in prev_sales:
					prevd = dt.created
				prevdate = DateFormat(prevd).format('Y-m-d')
				previous_sales_date = DateFormat(prevd).format('jS F Y')
			else:		
				prevdate = date
				previous_sales_date = selected_sales_date

			no_of_customers = Sales.objects.filter(created__contains=date).count()
			prevno_of_customers = Sales.objects.filter(created__contains=prevdate).count()
			try:
				customer_diff = int(((Decimal(no_of_customers) - Decimal(prevno_of_customers))/Decimal(prevno_of_customers))*100)
			except:
				customer_diff = 0

			date_total_sales = Sales.objects.filter(created__contains=date).aggregate(Sum('total_net'))['total_net__sum']
			prevdate_total_sales = Sales.objects.filter(created__contains=prevdate).aggregate(Sum('total_net'))['total_net__sum']
			try:
				sales_diff = int(((Decimal(date_total_sales) - Decimal(prevdate_total_sales))/Decimal(prevdate_total_sales))*100)
			except:
				sales_diff = 0
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
			# that date
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
			twentyone_twentytwo = get_hours_results(date, 21, 22)

			labels = ["7am","8am", "9am", "10am", "11am", "12am", "1pm",
			"2pm","3pm","4pm","5pm","6pm","7pm","8pm","9pm"]

			default = [seven_eight, eight_nine, nine_ten, ten_eleven, 
			eleven_twelve, twelve_thirteen, thriteen_fourteen, fourteen_fifteen, 
			fifteen_sixteen, sixteen_seventeen, seventeen_eighteen, 
			eighteen_nineteen, nineteen_twenty,twenty_twentyone]

			#previous date
			seven_eight2 = get_hours_results(prevdate, 7, 8)
			eight_nine2 = get_hours_results(prevdate, 8, 9)
			nine_ten2 = get_hours_results(prevdate, 9, 10)
			ten_eleven2 = get_hours_results(prevdate, 10, 11)
			eleven_twelve2 = get_hours_results(prevdate, 11, 12)
			twelve_thirteen2 = get_hours_results(prevdate, 12, 13)
			thriteen_fourteen2 = get_hours_results(prevdate, 13, 14)
			fourteen_fifteen2 = get_hours_results(prevdate, 14, 15)
			fifteen_sixteen2 = get_hours_results(prevdate, 15, 16)
			sixteen_seventeen2 = get_hours_results(prevdate, 16, 17)
			seventeen_eighteen2 = get_hours_results(prevdate, 17, 18)
			eighteen_nineteen2 = get_hours_results(prevdate, 18, 19)
			nineteen_twenty2 = get_hours_results(prevdate, 19, 20)
			twenty_twentyone2 = get_hours_results(prevdate, 20, 21)
			twentyone_twentytwo2 = get_hours_results(prevdate, 21, 22)


			labels2 = ["7am","8am", "9am", "10am", "11am", "12pm", "1pm",
			"2pm","3pm","4pm","5pm","6pm","7pm","8pm","9pm"]

			default2 = [seven_eight2, eight_nine2, nine_ten2, ten_eleven2, 
			eleven_twelve2, twelve_thirteen2, thriteen_fourteen2, fourteen_fifteen2, 
			fifteen_sixteen2, sixteen_seventeen2, seventeen_eighteen2, 
			eighteen_nineteen2, nineteen_twenty2,twenty_twentyone2, twentyone_twentytwo2]

			#get users in each teller and their total sales
			sales_that_day = Sales.objects.filter(created__contains=date)
			users_that_day = sales_that_day.values('user','user__email','total_net', 'created').annotate(c=Count('user__id', distinct=True))
			users = Sales.objects.values('user__email','user__name','terminal').annotate(Count('user')).annotate(Sum('total_net')).order_by().filter(created__contains=date)
			sales_by_category = SoldItem.objects.filter(sales__created__contains=date).values('product_category').annotate(c=Count('product_category', distinct=True)).annotate(Sum('total_cost')).order_by('-total_cost__sum')[:10]
			sales_by_category_totals = sales_by_category.aggregate(Sum('total_cost__sum'))['total_cost__sum__sum']
			new_sales = []
			for sales in sales_by_category:
				color = "#%03x" % random.randint(0, 0xFFF)
				sales['color'] = color
				percent = (Decimal(sales['total_cost__sum']) / Decimal(sales_by_category_totals)) * 100
				percentage = round(percent, 2)
				sales['percentage'] = percentage
				new_sales.append(sales)
			top_items = item_occurences.order_by('-total_cost__sum')[:5]
			data = {
				"highest_item": highest_item,
				"lowest_item":lowest_item,
				"no_of_customers":no_of_customers,
				"date_total_sales":date_total_sales,
				"popular_item":popular_item,
				"date":selected_sales_date,
				"prevdate":previous_sales_date,
				"labels":labels,
				"default":default,
				"labels2":labels2,
				"default2":default2,
				"cashiers":users_that_day,
				"users":users,
				"top_items":top_items,
				"sales_by_category":new_sales,
				"sales_percent":sales_diff,
				"customer_percent":customer_diff,
				"prevdate_total_sales":prev_sales
			}
			return TemplateResponse(request, 'dashboard/reports/sales/charts/by_date.html',data)
		except ObjectDoesNotExist as e:
			return TemplateResponse(request, 'dashboard/reports/sales/charts/by_date.html',{"error":e, "date":date})

def get_sales_by_week(request):
	date_from = request.GET.get('from')
	d_to = request.GET.get('to')
	date = d_to

	d = d_to.split('-')[-1]
	day_one = int(d)+1

	m = d_to.split('-')[-2]
	y = d_to.split('-')[-3]

	lastday_of_month = monthrange(int(y),int(m))[1]
	'''
		** - subtract number of days
	'''
	firstday_of_thisweek = datetime.datetime.strptime(date_from, '%Y-%m-%d')
	lastday_of_lastweek = firstday_of_thisweek - timedelta(days=(firstday_of_thisweek.weekday())+1)
	firstday_of_lastweek = lastday_of_lastweek - timedelta(days=7)
	# day differeces
	first_range_date = datetime.datetime.strptime(date_from, '%Y-%m-%d')
	second_range_date = datetime.datetime.strptime(d_to, '%Y-%m-%d')
	onedd = first_range_date + timedelta(days=1)
	'''
		s = Sales.objects.filter(created__year='2017', created__month='06', created__month__lte='08')
	'''
	date_range_diff = (second_range_date - first_range_date).days
	default3 = []
	labels3 = []
	if date_range_diff <= 8:
		for i in reversed(range(0, (date_range_diff)+1, 1)):
			p = (second_range_date) - timedelta(days=i)
			amount = get_date_results(DateFormat(p).format('Y-m-d'))
			day = str(p.strftime("%A")[0:3])+ ' ('+str(DateFormat(p).format('jS F'))+')'
			labels3.append(day)
			default3.append(amount)

	elif 8 < date_range_diff <= 10:
		for i in reversed(range(0, (date_range_diff)+1, 1)):
			p = (second_range_date) - timedelta(days=i)
			amount = get_date_results(DateFormat(p).format('Y-m-d'))
			day = str(p.strftime("%A")[0:3])+ ' (*'+str(DateFormat(p).format('jS'))+')'
			labels3.append(day)
			default3.append(amount)
	elif 20 < date_range_diff <= 31:
		for i in reversed(range(0, (date_range_diff)+1, 1)):
			p = (second_range_date) - timedelta(days=i)
			amount = get_date_results(DateFormat(p).format('Y-m-d'))
			day =  str(DateFormat(p).format('jS'))
			labels3.append(day)
			default3.append(amount)

	elif 360 < date_range_diff <= 365:
		date_range_diff

	if len(str(int(d))) == 1:
		date_to = date.replace(d_to[-2:], str('0'+str(day_one)))
	else:
		if int(d) == lastday_of_month:
			date_to = date.replace(d_to[-2:], str(d))
		else:
			date_to = date.replace(d_to[-2:], str(day_one))

	try:
		td_sales = Sales.objects.filter(created__contains=date).order_by('-id')[:1]
		if td_sales:
			for dt in td_sales:
				seld = dt.created
			selected_sales_date = DateFormat(seld).format('jS F Y')
		else:
			selected_sales_date = date
		prev_sales = Sales.objects.filter(created__lte=date)[:1]
		if prev_sales:
			for dt in prev_sales:
				prevd = dt.created
			prevdate = DateFormat(prevd).format('Y-m-d')
			previous_sales_date = DateFormat(prevd).format('jS F Y')
		else:		
			prevdate = date
			previous_sales_date = selected_sales_date

		no_of_customers = Sales.objects.filter(created__range=[date_from, date_to]).count()
		prevno_of_customers = Sales.objects.filter(created__month=str(int(m)-1)).count()
		try:
			customer_diff = int(((Decimal(no_of_customers) - Decimal(prevno_of_customers))/Decimal(prevno_of_customers))*100)
		except:
			customer_diff = 0

		date_total_sales = Sales.objects.filter(created__range=[date_from, date_to]).aggregate(Sum('total_net'))['total_net__sum']
		prevdate_total_sales = Sales.objects.filter(created__range=[(DateFormat(firstday_of_lastweek).format('Y-m-d')), (DateFormat(lastday_of_lastweek).format('Y-m-d')) ]).aggregate(Sum('total_net'))['total_net__sum']
		try:
			sales_diff = int(((Decimal(date_total_sales) - Decimal(prevdate_total_sales))/Decimal(prevdate_total_sales))*100)
		except:
			sales_diff = 0

		items = SoldItem.objects.filter(sales__created__range=[date_from, date_to])
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
		# that date
		seven_eight = get_hours_results_range(date_from, date_to, 7, 8)
		eight_nine = get_hours_results_range(date_from, date_to, 8, 9)
		nine_ten = get_hours_results_range(date_from, date_to, 9, 10)
		ten_eleven = get_hours_results_range(date_from, date_to, 10, 11)
		eleven_twelve = get_hours_results_range(date_from, date_to, 11, 12)
		twelve_thirteen = get_hours_results_range(date_from, date_to, 12, 13)
		thriteen_fourteen = get_hours_results_range(date_from, date_to, 13, 14)
		fourteen_fifteen = get_hours_results_range(date_from, date_to, 14, 15)
		fifteen_sixteen = get_hours_results_range(date_from, date_to, 15, 16)
		sixteen_seventeen = get_hours_results_range(date_from, date_to, 16, 17)
		seventeen_eighteen = get_hours_results_range(date_from, date_to, 17, 18)
		eighteen_nineteen = get_hours_results_range(date_from, date_to, 18, 19)
		nineteen_twenty = get_hours_results_range(date_from, date_to, 19, 20)
		twenty_twentyone = get_hours_results_range(date_from, date_to, 20, 21)
		twentyone_twentytwo = get_hours_results_range(date_from, date_to, 21, 22)

		labels = ["7am","8am", "9am", "10am", "11am", "12am", "1pm",
		"2pm","3pm","4pm","5pm","6pm","7pm","8pm","9pm"]

		default = [seven_eight, eight_nine, nine_ten, ten_eleven, 
		eleven_twelve, twelve_thirteen, thriteen_fourteen, fourteen_fifteen, 
		fifteen_sixteen, sixteen_seventeen, seventeen_eighteen, 
		eighteen_nineteen, nineteen_twenty,twenty_twentyone]

		#previous date
		seven_eight2 = get_hours_results(prevdate, 7, 8)
		eight_nine2 = get_hours_results(prevdate, 8, 9)
		nine_ten2 = get_hours_results(prevdate, 9, 10)
		ten_eleven2 = get_hours_results(prevdate, 10, 11)
		eleven_twelve2 = get_hours_results(prevdate, 11, 12)
		twelve_thirteen2 = get_hours_results(prevdate, 12, 13)
		thriteen_fourteen2 = get_hours_results(prevdate, 13, 14)
		fourteen_fifteen2 = get_hours_results(prevdate, 14, 15)
		fifteen_sixteen2 = get_hours_results(prevdate, 15, 16)
		sixteen_seventeen2 = get_hours_results(prevdate, 16, 17)
		seventeen_eighteen2 = get_hours_results(prevdate, 17, 18)
		eighteen_nineteen2 = get_hours_results(prevdate, 18, 19)
		nineteen_twenty2 = get_hours_results(prevdate, 19, 20)
		twenty_twentyone2 = get_hours_results(prevdate, 20, 21)
		twentyone_twentytwo2 = get_hours_results(prevdate, 21, 22)


		labels2 = ["7am","8am", "9am", "10am", "11am", "12pm", "1pm",
		"2pm","3pm","4pm","5pm","6pm","7pm","8pm","9pm"]

		default2 = [seven_eight2, eight_nine2, nine_ten2, ten_eleven2, 
		eleven_twelve2, twelve_thirteen2, thriteen_fourteen2, fourteen_fifteen2, 
		fifteen_sixteen2, sixteen_seventeen2, seventeen_eighteen2, 
		eighteen_nineteen2, nineteen_twenty2,twenty_twentyone2, twentyone_twentytwo2]

		#get users in each teller and their total sales
		sales_that_day = Sales.objects.filter(created__range=[date_from, date_to])
		users_that_day = sales_that_day.values('user','user__email','total_net', 'created').annotate(c=Count('user__id', distinct=True))
		users = Sales.objects.values('user__email','user__name','terminal').annotate(Count('user')).annotate(Sum('total_net')).order_by().filter(created__range=[date_from, date_to])
		sales_by_category = SoldItem.objects.filter(sales__created__range=[date_from, date_to]).values('product_category').annotate(c=Count('product_category', distinct=True)).annotate(Sum('total_cost')).order_by('-total_cost__sum')[:10]
		sales_by_category_totals = sales_by_category.aggregate(Sum('total_cost__sum'))['total_cost__sum__sum']
		new_sales = []
		for sales in sales_by_category:
			color = "#%03x" % random.randint(0, 0xFFF)
			sales['color'] = color
			percent = (Decimal(sales['total_cost__sum']) / Decimal(sales_by_category_totals)) * 100
			percentage = round(percent, 2)
			sales['percentage'] = percentage
			new_sales.append(sales)
		top_items = item_occurences.order_by('-total_cost__sum')[:5]
		data = {
			"highest_item": highest_item,
			"lowest_item":lowest_item,
			"no_of_customers":no_of_customers,
			"date_total_sales":date_total_sales,
			"popular_item":popular_item,
			"date":selected_sales_date,
			"prevdate":previous_sales_date,
			"labels":labels,
			"default":default,
			"labels2":labels2,
			"default2":default2,
			"labels3":labels3,
			"default3":default3,
			"cashiers":users_that_day,
			"users":users,
			"top_items":top_items,
			"sales_by_category":new_sales,
			"sales_percent":sales_diff,
			"customer_percent":customer_diff,
			"prevdate_total_sales":prev_sales
		}
		return TemplateResponse(request, 'dashboard/reports/sales/charts/by_date_range.html',data)
	except ObjectDoesNotExist as e:
		return TemplateResponse(request, 'dashboard/reports/sales/charts/by_date_range.html',{"error":e, "date":date})




def sales_user_chart(request):
	return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_user.html', {})

def sales_product_chart(request):
	return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_product.html', {})

def sales_teller_chart(request):
	return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_teller.html', {})