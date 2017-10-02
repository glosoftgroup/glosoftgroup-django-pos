import logging
import random
from decimal import Decimal
from calendar import monthrange
import calendar
import re
from django.template.response import TemplateResponse
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Min, Sum, Avg, Max
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from  datetime import *
from django.utils.dateformat import DateFormat

from ..views import staff_member_required
from ...credit.models import Credit
from ...sale.models import Sales, SoldItem, Terminal
from ...product.models import Category
from ...decorators import permission_decorator
from ...utils import render_to_pdf

from .hours_chart import get_item_results, get_terminal_results, get_user_results, get_hours_results, get_hours_results_range, get_date_results_range, get_date_results, get_category_results

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
def sales_category_chart(request, image=None):
	get_date = request.GET.get('date')
	today = datetime.datetime.now()
	if get_date:
		date = get_date
	else:
		try:
			last_sale = Sales.objects.latest('id')
			date = DateFormat(last_sale.created).format('Y-m-d')
		except:
			date = DateFormat(datetime.datetime.today()).format('Y-m-d')

	if image:
		dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
		ImageData = image
		ImageData = dataUrlPattern.match(ImageData).group(2)

		sales_by_category = SoldItem.objects.filter(sales__created__contains=date).values('product_category').annotate(
			c=Count('product_category', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by('-quantity__sum')[:5]
		quantity_totals = sales_by_category.aggregate(Sum('quantity__sum'))['quantity__sum__sum']
		new_sales = []
		for sales in sales_by_category:
			color = "#%03x" % random.randint(0, 0xFFF)
			sales['color'] = color
			percent = (Decimal(sales['quantity__sum']) / Decimal(quantity_totals)) * 100
			percentage = round(percent, 2)
			sales['percentage'] = percentage
			for s in range(0, sales_by_category.count(), 1):
				sales['count'] = s
			new_sales.append(sales)

		data = {
			'today': last_sale.created,
			'sales_by_category': new_sales,
			'puller': request.user,
			'image': ImageData,
		}
		pdf = render_to_pdf('dashboard/reports/sales/charts/pdf/category_pdf.html', data)
		return HttpResponse(pdf, content_type='application/pdf')

	if date:
		try:
			sales_by_category = SoldItem.objects.filter(sales__created__contains=date).values('product_category').annotate(
				c=Count('product_category', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by('-quantity__sum')
			quantity_totals = sales_by_category.aggregate(Sum('quantity__sum'))['quantity__sum__sum']
			new_sales = []
			for sales in sales_by_category:
				color = "#%03x" % random.randint(0, 0xFFF)
				sales['color'] = color
				percent = (Decimal(sales['quantity__sum']) / Decimal(quantity_totals)) * 100
				percentage = round(percent, 2)
				sales['percentage'] = percentage
				for s in range(0, sales_by_category.count(), 1):
					sales['count'] = s
				new_sales.append(sales)

			categs = Category.objects.all()
			this_year = today.year
			avg_m = Sales.objects.filter(created__year=this_year).annotate(c=Count('total_net'))
			highest_category_sales = new_sales[0]['product_category']
			default = []
			labels = []
			for i in range(1, (today.month + 1), 1):
				if len(str(i)) == 1:
					m =  str('0' + str(i))
				else:
					m = str(i)
				amount = get_category_results(highest_category_sales, str(today.year), m)
				labels.append(calendar.month_name[int(m)][0:3])
				default.append(amount)

			paginator = Paginator(new_sales, 5)
			new_sales2 = paginator.page(1)
			data = {
				"sales_by_category": new_sales2,
				"categs":categs,
				"avg":avg_m,
				"labels":labels,
				"default":default,
				"hcateg":highest_category_sales,
				"sales_date":date,
				"pn":paginator.num_pages,
				"count": sales_by_category.count()
			}
			return TemplateResponse(request, 'dashboard/reports/sales/ajax/category.html', data)
		except ObjectDoesNotExist as e:
			return TemplateResponse(request, 'dashboard/reports/sales/ajax/category.html', {"e":e, "date":date})
		except IndexError as e:
			return TemplateResponse(request, 'dashboard/reports/sales/ajax/category.html', {"e":e, "date":date})

def sales_category_chart_paginate(request):
	get_date = request.GET.get('date')
	page = request.GET.get('page', 1)
	list_sz = request.GET.get('size')
	if list_sz:
		size = list_sz
	else:
		size = 10
	if get_date:
		date = get_date
	else:
		try:
			last_sale = Sales.objects.latest('id')
			date = DateFormat(last_sale.created).format('Y-m-d')
		except:
			today = datetime.datetime.now()
			date = DateFormat(datetime.datetime.today()).format('Y-m-d')

	try:
		sales_by_category = SoldItem.objects.filter(sales__created__contains=date).values('product_category').annotate(
			c=Count('product_category', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
			'-quantity__sum')
		paginator = Paginator(sales_by_category, int(size))
		sales = paginator.page(page)
		data = {
			'sales_by_category': sales,
			'pn': paginator.num_pages, 'sz': size
		}
		return TemplateResponse(request, 'dashboard/reports/sales/ajax/cat_paginate.html', data)
	except ObjectDoesNotExist as e:
		return TemplateResponse(request, 'dashboard/reports/sales/ajax/cat_paginate.html', {"e": e, "date": date})
	except IndexError as e:
		return TemplateResponse(request, 'dashboard/reports/sales/ajax/cat_paginate.html', {"e": e, "date": date})



@staff_member_required
@permission_decorator('reports.view_sales_reports')
def get_category_sale_details(request):
	get_categ = request.GET.get('category')
	today = datetime.datetime.now()
	if get_categ:
		try:
			""" this year """
			this_year_sales = SoldItem.objects.filter(product_category__contains=get_categ, sales__created__year=today.year
												 ).aggregate(Sum('total_cost'))['total_cost__sum']
			y_sales = SoldItem.objects.filter(sales__created__year=today.year).aggregate(Sum('total_cost'))['total_cost__sum']
			try:
				ty_percent = round((Decimal(this_year_sales) / Decimal(y_sales)) * 100, 2)
				ty_others = 100 - ty_percent
			except:
				ty_percent = 0
				ty_others = 0

			""" this month """
			this_month_sales = SoldItem.objects.filter(product_category__contains=get_categ, sales__created__year=today.year,
													   sales__created__month=today.month).aggregate(Sum('total_cost'))['total_cost__sum']
			m_sales = SoldItem.objects.filter(sales__created__year=today.year, sales__created__month=today.month).aggregate(Sum('total_cost'))['total_cost__sum']
			try:
				tm_percent = round((Decimal(this_month_sales) / Decimal(m_sales)) * 100, 2)
				tm_others = 100 - tm_percent
			except:
				tm_percent = 0
				tm_others = 0

			""" last year """
			last_year_sales = SoldItem.objects.filter(product_category__contains=get_categ, sales__created__year=(today.year - 1)
													  ).aggregate(Sum('total_cost'))['total_cost__sum']
			ly_sales = SoldItem.objects.filter(sales__created__year=(today.year - 1)).aggregate(Sum('total_cost'))['total_cost__sum']
			try:
				ly_percent = round((Decimal(last_year_sales) / Decimal(ly_sales)) * 100, 2)
				ly_others = 100 - ly_percent
			except:
				ly_percent = 0
				ly_others = 0

			""" last month """
			last_month = today.month - 1 if today.month > 1 else 12
			last_month_sales = SoldItem.objects.filter(product_category__contains=get_categ, sales__created__year=today.year,
													   sales__created__month=last_month).aggregate(Sum('total_cost'))['total_cost__sum']

			lm_sales = SoldItem.objects.filter(sales__created__year=today.year, sales__created__month=last_month).aggregate(Sum('total_cost'))['total_cost__sum']
			try:
				lm_percent = round((Decimal(last_month_sales) / Decimal(lm_sales)) * 100, 2)
				lm_others = 100 - lm_percent
			except:
				lm_percent = 0
				lm_others = 0
			last_sales = SoldItem.objects.filter(product_category__contains=get_categ).values('product_category', 'total_cost','sales__created').annotate(Sum('total_cost', distinct=True)).order_by().latest('sales__id')


			data = {
				"category":get_categ,
				"this_year_sales": this_year_sales,
				"this_month_sales":this_month_sales,
				"last_year_sales":last_year_sales,
				"last_month_sales":last_month_sales,
				"ty_percent":ty_percent,
				"ty_others":ty_others,
				"tm_percent": tm_percent,
				"tm_others": tm_others,
				"ly_percent": ly_percent,
				"ly_others": ly_others,
				"lm_percent": lm_percent,
				"lm_others": lm_others,
				"last_sales":last_sales
			}
			return TemplateResponse(request, 'dashboard/reports/sales/charts/by_category.html', data)
		except ObjectDoesNotExist as e:
			return TemplateResponse(request, 'dashboard/reports/sales/charts/by_category.html',{})

@staff_member_required
@permission_decorator('reports.view_sales_reports')
def sales_date_chart(request, image=None):
	get_date = request.GET.get('date')
	if get_date:
		date = get_date
	else:
		try:
			last_sale = Sales.objects.latest('id')
			date = DateFormat(last_sale.created).format('Y-m-d')
		except:
			date = DateFormat(datetime.datetime.today()).format('Y-m-d')

	if image:
		dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
		ImageData = image
		ImageData = dataUrlPattern.match(ImageData).group(2)

		date_total_sales = Sales.objects.filter(created__contains=date).aggregate(Sum('total_net'))['total_net__sum']
		date_total_discount = Sales.objects.filter(created__contains=date).aggregate(Sum('discount_amount'))[
			'discount_amount__sum']
		date_total_tax = Sales.objects.filter(created__contains=date).aggregate(Sum('total_tax'))[
			'total_tax__sum']
		try:
			date_gross_sales = date_total_discount + date_total_tax + date_total_sales
		except:
			date_gross_sales = 0
		users = Sales.objects.values('user__email', 'user__name', 'terminal__terminal_name').annotate(Count('user')).annotate(
			Sum('total_net')).order_by().filter(created__contains=date)

		data = {
			'today': last_sale.created,
			'users': users,
			'puller': request.user,
			'image': ImageData,
			"date_total_sales": date_total_sales,
			"date_gross_sales": date_gross_sales,
			"date_total_tax": date_total_tax,
			"date_total_discount": date_total_discount,
		}
		pdf = render_to_pdf('dashboard/reports/sales/charts/pdf/pdf.html', data)
		return HttpResponse(pdf, content_type='application/pdf')

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
			date_total_discount = Sales.objects.filter(created__contains=date).aggregate(Sum('discount_amount'))[
				'discount_amount__sum']
			date_total_tax = Sales.objects.filter(created__contains=date).aggregate(Sum('total_tax'))[
				'total_tax__sum']

			prevdate_total_sales = Sales.objects.filter(created__contains=prevdate).aggregate(Sum('total_net'))['total_net__sum']
			try:
				sales_diff = int(((Decimal(date_total_sales) - Decimal(prevdate_total_sales))/Decimal(prevdate_total_sales))*100)
			except:
				sales_diff = 0
			items = SoldItem.objects.filter(sales__created__icontains=date)

			default =[]
			for i in range(7, 22):
				p = get_hours_results(date, i)
				default.append(p)

			labels = ["7am","8am", "9am", "10am", "11am", "12pm", "1pm",
			"2pm","3pm","4pm","5pm","6pm","7pm","8pm","9pm"]

			#get users in each teller and their total sales
			sales_that_day = Sales.objects.filter(created__contains=date)
			users_that_day = sales_that_day.values('user','user__email','total_net', 'created').annotate(c=Count('user__id', distinct=True))
			users = Sales.objects.values('user__email','user__name','terminal').annotate(Count('user')).annotate(Sum('total_net')).order_by().filter(created__contains=date)
			try:
				date_gross_sales = date_total_discount + date_total_tax + date_total_sales
			except:
				date_gross_sales = 0
			data = {
				"no_of_customers":no_of_customers,
				"date_total_sales":date_total_sales,
				"date_gross_sales":date_gross_sales,
				"date_total_tax":date_total_tax,
				"date_total_discount":date_total_discount,
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
			if get_date:
				return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_date.html',{"error":e, "date":date})
			else:
				return TemplateResponse(request, 'dashboard/reports/sales/charts/by_date.html',
										{"error": e, "date": date})

@staff_member_required
@permission_decorator('reports.view_sales_reports')
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

@staff_member_required
@permission_decorator('reports.view_sales_reports')
def get_sales_by_week(request):
	date_from = request.GET.get('from')
	d_to = request.GET.get('to')

	date = d_to
	d = d_to.split('-')[-1]
	day_one = int(d)+1
	m = d_to.split('-')[-2]
	y = d_to.split('-')[-3]

	lastday_of_month = monthrange(int(y),int(m))[1]
	# date convert
	first_range_date = datetime.strptime(date_from, '%Y-%m-%d')
	second_range_date = datetime.strptime(d_to, '%Y-%m-%d')

	default3 = []
	labels3 = []
	drf = (second_range_date - first_range_date) / 7
	for i in range(7):
		amount = get_date_results_range(DateFormat(i * drf + first_range_date).format('Y-m-d'), DateFormat((i+1)*drf+first_range_date).format('Y-m-d'))
		r = str((DateFormat(i * drf + first_range_date).format('d/m'))) + ' - ' + str(DateFormat((i+1)*drf+first_range_date).format('d/m'))
		labels3.append(r)
		default3.append(amount)

	if len(str(int(d))) == 1:
		if len(str(int(d)+1)) == 1:
			date_to = date.replace(d_to[-2:], str('0'+str(day_one)))
		else:
			date_to = date.replace(d_to[-2:], str(day_one))
	else:
		if int(d) == lastday_of_month:
			date_to = date.replace(d_to[-2:], str(d))
		else:
			date_to = date.replace(d_to[-2:], str(day_one))

	try:


		sales_customers = Sales.objects.filter(created__range=[date_from, date_to]).count()
		credit_customers = Credit.objects.filter(created__range=[date_from, date_to]).count()
		no_of_customers = sales_customers + credit_customers

		#get users in each teller and their total sales
		sales_that_day = Sales.objects.filter(created__range=[date_from, date_to]).aggregate(Sum('total_net'))['total_net__sum']
		users_that_day = Sales.objects.filter(created__range=[date_from, date_to]).values('user','user__email','total_net', 'created').annotate(c=Count('user__id', distinct=True))
		users = Sales.objects.values('user__email','user__name','terminal').annotate(Count('user')).annotate(Sum('total_net')).order_by().filter(created__range=[date_from, date_to])
		date_total_discount = Sales.objects.filter(created__range=[date_from, date_to]).aggregate(Sum('discount_amount'))[
			'discount_amount__sum']
		date_total_tax = Sales.objects.filter(created__range=[date_from, date_to]).aggregate(Sum('total_tax'))[
			'total_tax__sum']
		try:
			date_gross_sales = date_total_discount + date_total_tax + sales_that_day
		except:
			date_gross_sales = 0

		data = {
			"no_of_customers":no_of_customers,
			"date_total_sales":sales_that_day,
			"date_from":date_from,
			"date_to":date_to,
			"labels3":labels3,
			"default3":default3,
			"cashiers":users_that_day,
			"users":users,
			"date_gross_sales": date_gross_sales,
			"date_total_tax": date_total_tax,
			"date_total_discount": date_total_discount,
		}
		return TemplateResponse(request, 'dashboard/reports/sales/charts/by_date_range.html',data)
	except ObjectDoesNotExist as e:
		return TemplateResponse(request, 'dashboard/reports/sales/charts/by_date_range.html',{"error":e, "date":date})



@staff_member_required
@permission_decorator('reports.view_sale_reports')
def sales_user_chart(request):
	image = request.POST.get('img')
	today = datetime.datetime.now()
	get_date = request.GET.get('date')
	if get_date:
		date = get_date
	else:
		try:
			last_sale = Sales.objects.latest('id')
			date = DateFormat(last_sale.created).format('Y-m-d')
		except:
			date = DateFormat(datetime.datetime.today()).format('Y-m-d')

	if image:
		dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
		ImageData = image
		ImageData = dataUrlPattern.match(ImageData).group(2)

		users = Sales.objects.values('user__email', 'user__name', 'terminal').annotate(Count('user')).annotate(
			Sum('total_net')).order_by().filter(created__contains=date)
		sales_by_category_totals = users.aggregate(Sum('total_net__sum'))['total_net__sum__sum']
		new_sales = []
		for sales in users:
			color = "#%03x" % random.randint(0, 0xFFF)
			sales['color'] = color
			percent = (Decimal(sales['total_net__sum']) / Decimal(sales_by_category_totals)) * 100
			percentage = round(percent, 2)
			sales['percentage'] = percentage
			for s in range(0, users.count(), 1):
				sales['count'] = s
			new_sales.append(sales)

		data = {
			'today': last_sale.created,
			'sales_by_category': new_sales,
			'puller': request.user,
			'image': ImageData,
		}
		pdf = render_to_pdf('dashboard/reports/sales/charts/pdf/user_pdf.html', data)
		return HttpResponse(pdf, content_type='application/pdf')


	if date:
		try:
			users = Sales.objects.values('user__email', 'user__name', 'user').annotate(Count('user')).annotate(
				Sum('total_net')).annotate(
				Sum('solditems__quantity')).order_by('-solditems__quantity__sum').filter(created__contains=date)
			sales_by_category_totals = users.aggregate(Sum('solditems__quantity__sum'))['solditems__quantity__sum__sum']
			new_sales = []
			for sales in users:
				color = "#%03x" % random.randint(0, 0xFFF)
				sales['color'] = color
				percent = (Decimal(sales['solditems__quantity__sum']) / Decimal(sales_by_category_totals)) * 100
				percentage = round(percent, 2)
				sales['percentage'] = percentage
				for s in range(0, users.count(), 1):
					sales['count'] = s
				new_sales.append(sales)
			categs = Sales.objects.values('user__id','user__email', 'user__name').annotate(Count('user', distinct=True)).order_by()
			this_year = today.year
			avg_m = Sales.objects.filter(created__year=this_year).annotate(c=Count('total_net'))
			highest_user_sales = new_sales[0]['user__name']
			default = []
			labels = []
			for i in range(1, (today.month + 1), 1):
				if len(str(i)) == 1:
					m = str('0' + str(i))
				else:
					m = str(i)
				try:
					amount = get_user_results(highest_user_sales, str(today.year), m)
				except:
					amount = 0
				labels.append(calendar.month_name[int(m)][0:3])
				default.append(amount)

			paginator = Paginator(new_sales, 5)
			new_sales2 = paginator.page(1)

			data = {
				"sales_by_category": new_sales2,
				"categs": categs,
				"labels": labels,
				"default": default,
				"hcateg": highest_user_sales,
				"sales_date":date,
				"pn": paginator.num_pages,
				"count": users.count()
			}
			# return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_user.html', data)
			return TemplateResponse(request, 'dashboard/reports/sales/ajax/user.html', data)
		except ObjectDoesNotExist:
			return TemplateResponse(request, 'dashboard/reports/sales/ajax/user.html',{"sales_date":date})
		except IndexError:
			return TemplateResponse(request, 'dashboard/reports/sales/ajax/user.html',{"sales_date":date})

def sales_user_chart_paginate(request):
	get_date = request.GET.get('date')
	page = request.GET.get('page', 1)
	list_sz = request.GET.get('size')
	if list_sz:
		size = list_sz
	else:
		size = 10
	if get_date:
		date = get_date
	else:
		try:
			last_sale = Sales.objects.latest('id')
			date = DateFormat(last_sale.created).format('Y-m-d')
		except:
			today = datetime.datetime.now()
			date = DateFormat(datetime.datetime.today()).format('Y-m-d')

	try:
		users = Sales.objects.values('user__email', 'user__name', 'terminal').annotate(Count('user')).annotate(
			Sum('total_net')).annotate(
			Sum('solditems__quantity')).order_by('solditems__quantity__sum').filter(created__contains=date)
		paginator = Paginator(users, int(size))
		sales = paginator.page(page)
		data = {
			'sales_by_category': sales,
			'pn': paginator.num_pages, 'sz': size
		}
		return TemplateResponse(request, 'dashboard/reports/sales/ajax/user_paginate.html', data)
	except ObjectDoesNotExist as e:
		return TemplateResponse(request, 'dashboard/reports/sales/ajax/user_paginate.html', {"e": e, "date": date})
	except IndexError as e:
		return TemplateResponse(request, 'dashboard/reports/sales/ajax/user_paginate.html', {"e": e, "date": date})


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def get_user_sale_details(request):
	get_categ = request.GET.get('user')
	today = datetime.datetime.now()
	if get_categ:
		try:
			""" this year """
			this_year_sales = Sales.objects.filter(user__name__contains=get_categ, created__year=today.year
												 ).aggregate(Sum('total_net'))['total_net__sum']
			y_sales = Sales.objects.filter(created__year=today.year).aggregate(Sum('total_net'))['total_net__sum']
			try:
				ty_percent = round((Decimal(this_year_sales) / Decimal(y_sales)) * 100, 2)
				ty_others = 100 - ty_percent
			except:
				ty_percent = 0
				ty_others = 0

			""" this month """
			this_month_sales = Sales.objects.filter(user__name__contains=get_categ, created__year=today.year,
													   created__month=today.month).aggregate(Sum('total_net'))['total_net__sum']
			m_sales = Sales.objects.filter(created__year=today.year, created__month=today.month).aggregate(Sum('total_net'))['total_net__sum']
			try:
				tm_percent = round((Decimal(this_month_sales) / Decimal(m_sales)) * 100, 2)
				tm_others = 100 - tm_percent
			except:
				tm_percent = 0
				tm_others = 0

			""" last year """
			last_year_sales = Sales.objects.filter(user__name__contains=get_categ, created__year=(today.year - 1)
													  ).aggregate(Sum('total_net'))['total_net__sum']
			ly_sales = Sales.objects.filter(created__year=(today.year - 1)).aggregate(Sum('total_net'))['total_net__sum']
			try:
				ly_percent = round((Decimal(last_year_sales) / Decimal(ly_sales)) * 100, 2)
				ly_others = 100 - ly_percent
			except:
				ly_percent = 0
				ly_others = 0

			""" last month """
			last_month = today.month - 1 if today.month > 1 else 12
			last_month_sales = Sales.objects.filter(user__name__contains=get_categ, created__year=today.year,
													   created__month=last_month).aggregate(Sum('total_net'))['total_net__sum']

			lm_sales = Sales.objects.filter(created__year=today.year, created__month=last_month).aggregate(Sum('total_net'))['total_net__sum']
			try:
				lm_percent = round((Decimal(last_month_sales) / Decimal(lm_sales)) * 100, 2)
				lm_others = 100 - lm_percent
			except:
				lm_percent = 0
				lm_others = 0
			last_sales = Sales.objects.filter(user__name__contains=get_categ).values('user__name', 'total_net','created').annotate(Sum('total_net', distinct=True)).order_by().latest('id')

			data = {
				"category":get_categ,
				"this_year_sales": this_year_sales,
				"this_month_sales":this_month_sales,
				"last_year_sales":last_year_sales,
				"last_month_sales":last_month_sales,
				"ty_percent":ty_percent,
				"ty_others":ty_others,
				"tm_percent": tm_percent,
				"tm_others": tm_others,
				"ly_percent": ly_percent,
				"ly_others": ly_others,
				"lm_percent": lm_percent,
				"lm_others": lm_others,
				"last_sales":last_sales
			}
			return TemplateResponse(request, 'dashboard/reports/sales/charts/by_user.html', data)
		except ObjectDoesNotExist as e:
			return TemplateResponse(request, 'dashboard/reports/sales/charts/by_user.html',{})
			# return HttpResponse(e)

@staff_member_required
@permission_decorator('reports.view_sale_reports')
def sales_terminal_chart(request):
	image = request.POST.get('img')
	today = datetime.datetime.now()
	get_date = request.GET.get('date')
	if get_date:
		date = get_date
	else:
		try:
			last_sale = Sales.objects.latest('id')
			date = DateFormat(last_sale.created).format('Y-m-d')
		except:
			date = DateFormat(datetime.datetime.today()).format('Y-m-d')

	if image:
		dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
		ImageData = image
		ImageData = dataUrlPattern.match(ImageData).group(2)

		terminals = Sales.objects.values('terminal__terminal_name', 'terminal').annotate(Count('terminal')).annotate(
			Sum('total_net')).order_by().filter(created__contains=date)
		sales_by_category_totals = terminals.aggregate(Sum('total_net__sum'))['total_net__sum__sum']
		new_sales = []
		for sales in terminals:
			color = "#%03x" % random.randint(0, 0xFFF)
			sales['color'] = color
			percent = (Decimal(sales['total_net__sum']) / Decimal(sales_by_category_totals)) * 100
			percentage = round(percent, 2)
			sales['percentage'] = percentage
			for s in range(0, terminals.count(), 1):
				sales['count'] = s
			new_sales.append(sales)

		data = {
			'today': last_sale.created,
			'sales_by_category': new_sales,
			'puller': request.user,
			'image': ImageData,
		}
		pdf = render_to_pdf('dashboard/reports/sales/charts/pdf/terminal_pdf.html', data)
		return HttpResponse(pdf, content_type='application/pdf')


	if date:
		try:
			terminals = Sales.objects.values('terminal__terminal_name', 'terminal').annotate(Count('terminal')).annotate(
				Sum('solditems__quantity')).annotate(Sum('total_net')).order_by('-solditems__quantity__sum').filter(created__contains = date)
			sales_by_category_totals = terminals.aggregate(Sum('solditems__quantity__sum'))['solditems__quantity__sum__sum']
			new_sales = []
			for sales in terminals:
				color = "#%03x" % random.randint(0, 0xFFF)
				sales['color'] = color
				percent = (Decimal(sales['solditems__quantity__sum']) / Decimal(sales_by_category_totals)) * 100
				percentage = round(percent, 2)
				sales['percentage'] = percentage
				for s in range(0, terminals.count(), 1):
					sales['count'] = s
				new_sales.append(sales)
			categs =  Terminal.objects.all()
			this_year = today.year
			avg_m = Sales.objects.filter(created__year=this_year).annotate(c=Count('total_net'))
			highest_user_sales = new_sales[0]['terminal__terminal_name']
			default = []
			labels = []
			for i in range(1, (today.month + 1), 1):
				if len(str(i)) == 1:
					m = str('0' + str(i))
				else:
					m = str(i)
				amount = get_terminal_results(highest_user_sales, str(today.year), m)
				labels.append(calendar.month_name[int(m)][0:3])
				default.append(amount)

			paginator = Paginator(new_sales, 5)
			new_sales2 = paginator.page(1)
			data = {
				"sales_by_category": new_sales2,
				"categs": categs,
				"labels": labels,
				"default": default,
				"hcateg": highest_user_sales,
				"sales_date":date,
				"pn": paginator.num_pages,
				"count": terminals.count()
			}
			# return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_teller.html', data)
			return TemplateResponse(request, 'dashboard/reports/sales/ajax/till.html', data)
		except ObjectDoesNotExist:
			return TemplateResponse(request, 'dashboard/reports/sales/ajax/till.html',{"sales_date":date})
		except IndexError:
			return TemplateResponse(request, 'dashboard/reports/sales/ajax/till.html',{"sales_date":date})

def sales_till_chart_paginate(request):
	get_date = request.GET.get('date')
	page = request.GET.get('page', 1)
	list_sz = request.GET.get('size')
	if list_sz:
		size = list_sz
	else:
		size = 10
	if get_date:
		date = get_date
	else:
		try:
			last_sale = Sales.objects.latest('id')
			date = DateFormat(last_sale.created).format('Y-m-d')
		except:
			today = datetime.datetime.now()
			date = DateFormat(datetime.datetime.today()).format('Y-m-d')

	try:
		terminals = Sales.objects.values('terminal__terminal_name', 'terminal').annotate(Count('terminal')).annotate(
			Sum('solditems__quantity')).annotate(Sum('total_net')).order_by('solditems__quantity__sum').filter(
			created__contains=date)
		paginator = Paginator(terminals, int(size))
		sales = paginator.page(page)
		data = {
			'sales_by_category': sales,
			'pn': paginator.num_pages, 'sz': size
		}
		return TemplateResponse(request, 'dashboard/reports/sales/ajax/till_paginate.html', data)
	except ObjectDoesNotExist as e:
		return TemplateResponse(request, 'dashboard/reports/sales/ajax/till_paginate.html', {"e": e, "date": date})
	except IndexError as e:
		return TemplateResponse(request, 'dashboard/reports/sales/ajax/till_paginate.html', {"e": e, "date": date})


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def get_terminal_sale_details(request):
	get_categ = request.GET.get('terminal')
	today = datetime.datetime.now()
	if get_categ:
		try:
			""" this year """
			this_year_sales = Sales.objects.filter(terminal__terminal_name__contains=get_categ, created__year=today.year
												 ).aggregate(Sum('total_net'))['total_net__sum']
			y_sales = Sales.objects.filter(created__year=today.year).aggregate(Sum('total_net'))['total_net__sum']
			try:
				ty_percent = round((Decimal(this_year_sales) / Decimal(y_sales)) * 100, 2)
				ty_others = 100 - ty_percent
			except:
				ty_percent = 0
				ty_others = 0

			""" this month """
			this_month_sales = Sales.objects.filter(terminal__terminal_name__contains=get_categ, created__year=today.year,
													   created__month=today.month).aggregate(Sum('total_net'))['total_net__sum']
			m_sales = Sales.objects.filter(created__year=today.year, created__month=today.month).aggregate(Sum('total_net'))['total_net__sum']
			try:
				tm_percent = round((Decimal(this_month_sales) / Decimal(m_sales)) * 100, 2)
				tm_others = 100 - tm_percent
			except:
				tm_percent = 0
				tm_others = 0

			""" last year """
			last_year_sales = Sales.objects.filter(terminal__terminal_name__contains=get_categ, created__year=(today.year - 1)
													  ).aggregate(Sum('total_net'))['total_net__sum']
			ly_sales = Sales.objects.filter(created__year=(today.year - 1)).aggregate(Sum('total_net'))['total_net__sum']
			try:
				ly_percent = round((Decimal(last_year_sales) / Decimal(ly_sales)) * 100, 2)
				ly_others = 100 - ly_percent
			except:
				ly_percent = 0
				ly_others = 0

			""" last month """
			last_month = today.month - 1 if today.month > 1 else 12
			last_month_sales = Sales.objects.filter(terminal__terminal_name__contains=get_categ, created__year=today.year,
													   created__month=last_month).aggregate(Sum('total_net'))['total_net__sum']

			lm_sales = Sales.objects.filter(created__year=today.year, created__month=last_month).aggregate(Sum('total_net'))['total_net__sum']
			try:
				lm_percent = round((Decimal(last_month_sales) / Decimal(lm_sales)) * 100, 2)
				lm_others = 100 - lm_percent
			except:
				lm_percent = 0
				lm_others = 0
			last_sales = Sales.objects.filter(terminal__terminal_name__contains=get_categ).values('terminal__terminal_name', 'total_net','created').annotate(Sum('total_net', distinct=True)).order_by().latest('id')

			data = {
				"category":get_categ,
				"this_year_sales": this_year_sales,
				"this_month_sales":this_month_sales,
				"last_year_sales":last_year_sales,
				"last_month_sales":last_month_sales,
				"ty_percent":ty_percent,
				"ty_others":ty_others,
				"tm_percent": tm_percent,
				"tm_others": tm_others,
				"ly_percent": ly_percent,
				"ly_others": ly_others,
				"lm_percent": lm_percent,
				"lm_others": lm_others,
				"last_sales":last_sales
			}
			return TemplateResponse(request, 'dashboard/reports/sales/charts/by_terminal.html', data)
		except ObjectDoesNotExist as e:
			return TemplateResponse(request, 'dashboard/reports/sales/charts/by_terminal.html',{})

@staff_member_required
@permission_decorator('reports.view_products_reports')
def sales_product_chart(request):
	get_date = request.GET.get('date')
	image = request.POST.get('img')
	today = datetime.datetime.now()
	if get_date:
		date = get_date
	else:
		try:
			last_sale = Sales.objects.latest('id')
			date = DateFormat(last_sale.created).format('Y-m-d')
		except:
			date = DateFormat(datetime.datetime.today()).format('Y-m-d')

	if image:
		dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
		ImageData = image
		ImageData = dataUrlPattern.match(ImageData).group(2)

		sales_by_category = SoldItem.objects.filter(sales__created__contains=date).values('product_category').annotate(
			c=Count('product_category', distinct=True)).annotate(Sum('total_cost')).order_by('-total_cost__sum')[:5]
		sales_by_category_totals = sales_by_category.aggregate(Sum('total_cost__sum'))['total_cost__sum__sum']
		new_sales = []
		for sales in sales_by_category:
			color = "#%03x" % random.randint(0, 0xFFF)
			sales['color'] = color
			percent = (Decimal(sales['total_cost__sum']) / Decimal(sales_by_category_totals)) * 100
			percentage = round(percent, 2)
			sales['percentage'] = percentage
			for s in range(0, sales_by_category.count(), 1):
				sales['count'] = s
			new_sales.append(sales)

		data = {
			'today': last_sale.created,
			'sales_by_category': new_sales,
			'puller': request.user,
			'image': ImageData,
		}
		pdf = render_to_pdf('dashboard/reports/sales/charts/pdf/product_pdf.html', data)
		return HttpResponse(pdf, content_type='application/pdf')
	if date:
		try:
			sales_by_category = SoldItem.objects.filter(sales__created__contains=date).values('product_name').annotate(
				c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by('-quantity__sum')

			quantity_totals = sales_by_category.aggregate(Sum('quantity__sum'))['quantity__sum__sum']
			new_sales = []
			for sales in sales_by_category:
				color = "#%03x" % random.randint(0, 0xFFF)
				sales['color'] = color
				percent = (Decimal(sales['quantity__sum']) / Decimal(quantity_totals)) * 100
				percentage = round(percent, 2)
				sales['percentage'] = percentage
				for s in range(0, sales_by_category.count(), 1):
					sales['count'] = s
				new_sales.append(sales)
			categs = SoldItem.objects.values('product_name').annotate(Count('product_name', distinct=True)).order_by()
			this_year = today.year
			avg_m = Sales.objects.filter(created__year=this_year).annotate(c=Count('total_net'))
			highest_category_sales = new_sales[0]['product_name']
			default = []
			labels = []
			for i in range(1, (today.month + 1), 1):
				if len(str(i)) == 1:
					m =  str('0' + str(i))
				else:
					m = str(i)
				amount = get_item_results(highest_category_sales, str(today.year), m)
				labels.append(calendar.month_name[int(m)][0:3])
				default.append(amount)

			paginator = Paginator(new_sales, 5)
			new_sales2 = paginator.page(1)

			data = {
				"sales_by_category": new_sales2,
				"categs":categs,
				"avg":avg_m,
				"labels":labels,
				"default":default,
				"hcateg":highest_category_sales,
				"sales_date":date,
				"pn":paginator.num_pages,
				"count":sales_by_category.count()
			}
			# return TemplateResponse(request, 'dashboard/reports/sales/charts/sales_by_product.html', data)
			return TemplateResponse(request, 'dashboard/reports/sales/ajax/items.html', data)
		except ObjectDoesNotExist as e:
			return TemplateResponse(request, 'dashboard/reports/sales/ajax/items.html',{'sales_date':date})
		except IndexError as e:
			return TemplateResponse(request, 'dashboard/reports/sales/ajax/items.html',{'sales_date':date})

def sales_product_chart_paginate(request):
	get_date = request.GET.get('date')
	page = request.GET.get('page', 1)
	list_sz = request.GET.get('size')
	if list_sz:
		size = list_sz
	else:
		size = 10
	if get_date:
		date = get_date
	else:
		try:
			last_sale = Sales.objects.latest('id')
			date = DateFormat(last_sale.created).format('Y-m-d')
		except:
			today = datetime.datetime.now()
			date = DateFormat(datetime.datetime.today()).format('Y-m-d')

	try:
		sales_by_category = SoldItem.objects.filter(sales__created__contains=date).values('product_name').annotate(
			c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
			'-quantity__sum')
		paginator = Paginator(sales_by_category, int(size))
		sales = paginator.page(page)
		data = {
			'sales_by_category': sales,
			'pn': paginator.num_pages, 'sz': size
		}
		return TemplateResponse(request, 'dashboard/reports/sales/ajax/item_paginate.html', data)
	except ObjectDoesNotExist as e:
		return TemplateResponse(request, 'dashboard/reports/sales/ajax/item_paginate.html', {"e": e, "date": date})
	except IndexError as e:
		return TemplateResponse(request, 'dashboard/reports/sales/ajax/item_paginate.html', {"e": e, "date": date})


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def get_product_sale_details(request):
	get_categ = request.GET.get('item')
	today = datetime.datetime.now()
	if get_categ:
		try:
			""" this year """
			this_year_sales = SoldItem.objects.filter(product_name__contains=get_categ, sales__created__year=today.year
												 ).aggregate(Sum('total_cost'))['total_cost__sum']
			y_sales = SoldItem.objects.filter(sales__created__year=today.year).aggregate(Sum('total_cost'))['total_cost__sum']
			try:
				ty_percent = round((Decimal(this_year_sales) / Decimal(y_sales)) * 100, 2)
				ty_others = 100 - ty_percent
			except:
				ty_percent = 0
				ty_others = 0

			""" this month """
			this_month_sales = SoldItem.objects.filter(product_name__contains=get_categ, sales__created__year=today.year,
													   sales__created__month=today.month).aggregate(Sum('total_cost'))['total_cost__sum']
			m_sales = SoldItem.objects.filter(sales__created__year=today.year, sales__created__month=today.month).aggregate(Sum('total_cost'))['total_cost__sum']
			try:
				tm_percent = round((Decimal(this_month_sales) / Decimal(m_sales)) * 100, 2)
				tm_others = 100 - tm_percent
			except:
				tm_percent = 0
				tm_others = 0

			""" last year """
			last_year_sales = SoldItem.objects.filter(product_name__contains=get_categ, sales__created__year=(today.year - 1)
													  ).aggregate(Sum('total_cost'))['total_cost__sum']
			ly_sales = SoldItem.objects.filter(sales__created__year=(today.year - 1)).aggregate(Sum('total_cost'))['total_cost__sum']
			try:
				ly_percent = round((Decimal(last_year_sales) / Decimal(ly_sales)) * 100, 2)
				ly_others = 100 - ly_percent
			except:
				ly_percent = 0
				ly_others = 0

			""" last month """
			last_month = today.month - 1 if today.month > 1 else 12
			last_month_sales = SoldItem.objects.filter(product_name__contains=get_categ, sales__created__year=today.year,
													   sales__created__month=last_month).aggregate(Sum('total_cost'))['total_cost__sum']

			lm_sales = SoldItem.objects.filter(sales__created__year=today.year, sales__created__month=last_month).aggregate(Sum('total_cost'))['total_cost__sum']
			try:
				lm_percent = round((Decimal(last_month_sales) / Decimal(lm_sales)) * 100, 2)
				lm_others = 100 - lm_percent
			except:
				lm_percent = 0
				lm_others = 0
			last_sales = SoldItem.objects.filter(product_name__contains=get_categ).values('product_name', 'total_cost','sales__created').annotate(Sum('total_cost', distinct=True)).order_by().latest('sales__id')


			data = {
				"category":get_categ,
				"this_year_sales": this_year_sales,
				"this_month_sales":this_month_sales,
				"last_year_sales":last_year_sales,
				"last_month_sales":last_month_sales,
				"ty_percent":ty_percent,
				"ty_others":ty_others,
				"tm_percent": tm_percent,
				"tm_others": tm_others,
				"ly_percent": ly_percent,
				"ly_others": ly_others,
				"lm_percent": lm_percent,
				"lm_others": lm_others,
				"last_sales":last_sales
			}
			return TemplateResponse(request, 'dashboard/reports/sales/charts/by_product.html', data)
		except ObjectDoesNotExist as e:
			return TemplateResponse(request, 'dashboard/reports/sales/charts/by_product.html',{})
			# return HttpResponse(e)


# discount
@staff_member_required
@permission_decorator('reports.view_products_reports')
def sales_discount_chart(request):
	get_date = request.GET.get('date')
	image = request.POST.get('img')
	today = datetime.datetime.now()
	if get_date:
		date = get_date
	else:
		try:
			last_sale = Sales.objects.filter(~Q(discount_amount = 0.00)).latest('id')
			date = DateFormat(last_sale.created).format('Y-m-d')
		except:
			date = DateFormat(datetime.datetime.today()).format('Y-m-d')

	if image:
		dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
		ImageData = image
		ImageData = dataUrlPattern.match(ImageData).group(2)

		sales_by_category = SoldItem.objects.filter(sales__created__contains=date).filter(~Q(discount = 0.00)).values('product_category').annotate(
			c=Count('product_category', distinct=True)).annotate(Sum('total_cost')).order_by('-total_cost__sum')[:5]
		sales_by_category_totals = sales_by_category.aggregate(Sum('total_cost__sum'))['total_cost__sum__sum']
		new_sales = []
		for sales in sales_by_category:
			color = "#%03x" % random.randint(0, 0xFFF)
			sales['color'] = color
			percent = (Decimal(sales['total_cost__sum']) / Decimal(sales_by_category_totals)) * 100
			percentage = round(percent, 2)
			sales['percentage'] = percentage
			for s in range(0, sales_by_category.count(), 1):
				sales['count'] = s
			new_sales.append(sales)

		data = {
			'today': last_sale.created,
			'sales_by_category': new_sales,
			'puller': request.user,
			'image': ImageData,
		}
		pdf = render_to_pdf('dashboard/reports/sales/charts/pdf/product_pdf.html', data)
		return HttpResponse(pdf, content_type='application/pdf')
	if date:
		try:
			sales_by_category = SoldItem.objects.filter(sales__created__contains=date).filter(~Q(discount = 0.00)).values('product_name','discount').annotate(
				c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by('-quantity__sum')

			quantity_totals = sales_by_category.aggregate(Sum('quantity__sum'))['quantity__sum__sum']
			new_sales = []
			for sales in sales_by_category:
				color = "#%03x" % random.randint(0, 0xFFF)
				sales['color'] = color
				percent = (Decimal(sales['quantity__sum']) / Decimal(quantity_totals)) * 100
				percentage = round(percent, 2)
				sales['percentage'] = percentage
				for s in range(0, sales_by_category.count(), 1):
					sales['count'] = s
				new_sales.append(sales)
			categs = SoldItem.objects.values('product_name','discount').annotate(Count('product_name', distinct=True)).order_by()
			this_year = today.year
			avg_m = Sales.objects.filter(created__year=this_year).filter(~Q(discount_amount = 0.00)).annotate(c=Count('total_net'))
			highest_category_sales = new_sales[0]['product_name']
			default = []
			labels = []
			for i in range(1, (today.month + 1), 1):
				if len(str(i)) == 1:
					m =  str('0' + str(i))
				else:
					m = str(i)
				amount = get_item_results(highest_category_sales, str(today.year), m)
				labels.append(calendar.month_name[int(m)][0:3])
				default.append(amount)

			paginator = Paginator(new_sales, 5)
			new_sales2 = paginator.page(1)

			data = {
				"sales_by_category": new_sales2,
				"categs":categs,
				"avg":avg_m,
				"labels":labels,
				"default":default,
				"hcateg":highest_category_sales,
				"sales_date":date,
				"pn":paginator.num_pages,
				"count":sales_by_category.count()
			}
			
			return TemplateResponse(request, 'dashboard/reports/sales/ajax/discount.html', data)
		except ObjectDoesNotExist as e:
			return TemplateResponse(request, 'dashboard/reports/sales/ajax/discount.html',{'sales_date':date})
		except IndexError as e:
			return TemplateResponse(request, 'dashboard/reports/sales/ajax/items.html',{'sales_date':date})

def sales_discount_chart_paginate(request):
	get_date = request.GET.get('date')
	page = request.GET.get('page', 1)
	list_sz = request.GET.get('size')
	if list_sz:
		size = list_sz
	else:
		size = 10
	if get_date:
		date = get_date
	else:
		try:
			last_sale = Sales.objects.filter(~Q(discount_amount = 0.00)).latest('id')
			date = DateFormat(last_sale.created).format('Y-m-d')
		except:
			today = datetime.datetime.now()
			date = DateFormat(datetime.datetime.today()).format('Y-m-d')

	try:
		sales_by_category = SoldItem.objects.filter(sales__created__contains=date).filter(~Q(discount = 0.00)).values('product_name','discount').annotate(
			c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
			'-quantity__sum')
		paginator = Paginator(sales_by_category, int(size))
		sales = paginator.page(page)
		data = {
			'sales_by_category': sales,
			'pn': paginator.num_pages, 'sz': size
		}
		return TemplateResponse(request, 'dashboard/reports/sales/ajax/discount_paginate.html', data)
	except ObjectDoesNotExist as e:
		return TemplateResponse(request, 'dashboard/reports/sales/ajax/discount_paginate.html', {"e": e, "date": date})
	except IndexError as e:
		return TemplateResponse(request, 'dashboard/reports/sales/ajax/discount_paginate.html', {"e": e, "date": date})

