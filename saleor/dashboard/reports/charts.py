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
from ...sale.models import Sales, SoldItem, Terminal
from ...product.models import Product, ProductVariant
from ...decorators import permission_decorator, user_trail
from ...utils import render_to_pdf, convert_html_to_pdf

from .hours_chart import get_hours_results, get_hours_results_range, get_date_results_range, get_date_results

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
def sales_date_chart(request):
	get_date = request.GET.get('date')
	if get_date:
		date = get_date
	else:
		last_sale = Sales.objects.latest('id')
		date = DateFormat(last_sale.created).format('Y-m-d')

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

			# that date
			seven_eight = get_hours_results(date, 7, 8)
			eight_nine = get_hours_results(date, 8, 9)
			nine_ten = get_hours_results(date, 9, 10)
			ten_eleven = get_hours_results(date, 10, 11)
			eleven_twelve = get_hours_results(date, 11, 12)
			twelve_thirteen = get_hours_results(date, 12, 13)
			thirteen_fourteen = get_hours_results(date, 13, 14)
			fourteen_fifteen = get_hours_results(date, 14, 15)
			fifteen_sixteen = get_hours_results(date, 15, 16)
			sixteen_seventeen = get_hours_results(date, 16, 17)
			seventeen_eighteen = get_hours_results(date, 17, 18)
			eighteen_nineteen = get_hours_results(date, 18, 19)
			nineteen_twenty = get_hours_results(date, 19, 20)
			twenty_twentyone = get_hours_results(date, 20, 21)
			twentyone_twentytwo = get_hours_results(date, 21, 22)

			default = [seven_eight, eight_nine, nine_ten, ten_eleven,
			eleven_twelve, twelve_thirteen, thirteen_fourteen, fourteen_fifteen,
			fifteen_sixteen, sixteen_seventeen, seventeen_eighteen,
			eighteen_nineteen, nineteen_twenty,twenty_twentyone]

			labels = ["7am","8am", "9am", "10am", "11am", "12pm", "1pm",
			"2pm","3pm","4pm","5pm","6pm","7pm","8pm","9pm"]

			#get users in each teller and their total sales
			sales_that_day = Sales.objects.filter(created__contains=date)
			users_that_day = sales_that_day.values('user','user__email','total_net', 'created').annotate(c=Count('user__id', distinct=True))
			users = Sales.objects.values('user__email','user__name','terminal').annotate(Count('user')).annotate(Sum('total_net')).order_by().filter(created__contains=date)
			data = {
				"no_of_customers":no_of_customers,
				"date_total_sales":date_total_sales,
				"date":selected_sales_date,
				"prevdate":previous_sales_date,
				"default":default,
				"labels2":labels,
				"cashiers":users_that_day,
				"users":users,
				"sales_percent":sales_diff,
				"customer_percent":customer_diff,
				"prevdate_total_sales":prev_sales,
				"previous_sales":prevdate_total_sales,
			}
			if get_date:
				return TemplateResponse(request, 'dashboard/reports/sales/charts/by_date.html', data)
			else:
				return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_date.html',data)
		except ObjectDoesNotExist as e:
			return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_date.html',{"error":e, "date":date})


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

	elif date_range_diff >= 60:
		c = [first_range_date+timedelta(days=i) for i in range(0,(date_range_diff+1),30)]
		r = (second_range_date-c[-1]).days
		if r == 0:
			for i in range(0, (date_range_diff) + 1, 30):
				p = first_range_date + timedelta(days=i)
				p_next = p + timedelta(days=30)
				amount = get_date_results_range(DateFormat(p).format('Y-m-d'), DateFormat(p_next).format('Y-m-d'))
				r = str((DateFormat(p).format('d/m'))) + ' - ' + str(DateFormat(p_next).format('d/m'))
				labels3.append(r)
				default3.append(amount)
		else:
			# c.append(second_range_date)
			for i in c:
				# p = first_range_date + timedelta(days=i)
				p_next = i + timedelta(days=30)
				amount = get_date_results_range(DateFormat(i).format('Y-m-d'), DateFormat(p_next).format('Y-m-d'))
				r = str((DateFormat(i).format('d/m'))) + ' - ' + str(DateFormat(p_next).format('d/m'))
				labels3.append(r)
				default3.append(amount)



	elif date_range_diff >= 150:
		for i in range(0, (date_range_diff)+1, 30):
			p = (first_range_date) + timedelta(days=i)
			p_next = p+timedelta(days=30)
			amount = get_date_results_range(DateFormat(p).format('Y-m-d'), DateFormat(p_next).format('Y-m-d'))
			r = str((DateFormat(p).format('d'))) +'.'+str(p.strftime("%b")[0:2])+' - '+str(DateFormat(p_next).format('d')+'.'+str(p_next.strftime("%b")[0:2]))
			labels3.append(r)
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


		no_of_customers = Sales.objects.filter(created__range=[date_from, date_to]).count()

		items = SoldItem.objects.filter(sales__created__range=[date_from, date_to])

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

		labels2 = ["7am","8am", "9am", "10am", "11am", "12pm", "1pm",
		"2pm","3pm","4pm","5pm","6pm","7pm","8pm","9pm"]

		#get users in each teller and their total sales
		sales_that_day = Sales.objects.filter(created__range=[date_from, date_to]).aggregate(Sum('total_net'))['total_net__sum']
		users_that_day = Sales.objects.filter(created__range=[date_from, date_to]).values('user','user__email','total_net', 'created').annotate(c=Count('user__id', distinct=True))
		users = Sales.objects.values('user__email','user__name','terminal').annotate(Count('user')).annotate(Sum('total_net')).order_by().filter(created__range=[date_from, date_to])

		data = {
			"no_of_customers":no_of_customers,
			"date_total_sales":sales_that_day,
			"date_from":date_from,
			"date_to":date_to,
			"default":default,
			"labels2":labels2,
			"labels3":labels3,
			"default3":default3,
			"cashiers":users_that_day,
			"users":users
		}
		return TemplateResponse(request, 'dashboard/reports/sales/charts/by_date_range.html',data)
	except ObjectDoesNotExist as e:
		return TemplateResponse(request, 'dashboard/reports/sales/charts/by_date_range.html',{"error":e, "date":date})




def sales_user_chart(request):
	return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_user.html', {})

def sales_product_chart(request):
	return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_product.html', {})

def sales_teller_chart(request):
	terminals = Terminal.objects.all()
	return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_teller.html', {"terminals":terminals})