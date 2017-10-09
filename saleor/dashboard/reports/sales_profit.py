from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.utils.dateformat import DateFormat
import datetime
import dateutil.relativedelta

from ..views import staff_member_required
from ...sale.models import Sales, SoldItem
from ...product.models import ProductVariant
from ...utils import render_to_pdf, image64
from ...accounts.models import *

def get_pettycash_expenses(year, month=None):
	if year and month:
		expenses = Expenses.objects.filter(added_on__year=year, added_on__month=month).aggregate(Sum('amount'))['amount__sum']
		if expenses is None:
			expenses = 0
	elif year:
		expenses = Expenses.objects.filter(added_on__year=year).aggregate(Sum('amount'))['amount__sum']
		if expenses is None:
			expenses = 0

	return {
		'expenses':expenses
	}
def get_total_expenses(year, month=None):
	if year and month:
		try:
			expenses = PersonalExpenses.objects.filter(added_on__year=year, added_on__month=month).aggregate(Sum('amount'))['amount__sum']
			if expenses is None:
				expenses = 0
		except:
			expenses = 0

		try:
			petty = Expenses.objects.filter(added_on__year=year, added_on__month=month).aggregate(Sum('amount'))['amount__sum']
			if petty is None:
				petty = 0
		except:
			petty = 0

		total = expenses + petty
	elif year:
		try:
			expenses = PersonalExpenses.objects.filter(added_on__year=year).aggregate(Sum('amount'))['amount__sum']
			if expenses is None:
				expenses = 0
		except:
			expenses = 0

		try:
			petty = Expenses.objects.filter(added_on__year=year).aggregate(Sum('amount'))[
				'amount__sum']
			if petty is None:
				petty = 0
		except:
			petty = 0

		total = expenses + petty

	return {
		'expenses': total
	}

def sales_period_results(year, month=None):
	if year and month:
		sales = Sales.objects.filter(created__year=year, created__month=month)
		soldItems = SoldItem.objects.filter(sales__created__year=year, sales__created__month=month).order_by('-id')
		totalSales = sales.aggregate(Sum('total_net'))['total_net__sum']
		totalTax = sales.aggregate(Sum('total_tax'))['total_tax__sum']
		expenses = PersonalExpenses.objects.filter(added_on__year=year, added_on__month=month)
	elif year:
		sales = Sales.objects.filter(created__year=year)
		soldItems = SoldItem.objects.filter(sales__created__year=year).order_by('-id')
		totalSales = sales.aggregate(Sum('total_net'))['total_net__sum']
		totalTax = sales.aggregate(Sum('total_tax'))['total_tax__sum']
		expenses = PersonalExpenses.objects.filter(added_on__year=year).aggregate(Sum('amount'))['amount__sum']

	costPrice = []
	for i in soldItems:
		product = ProductVariant.objects.get(sku=i.sku)
		try:
			quantity = product.get_cost_price().gross
		except ValueError, e:
			quantity = product.get_cost_price()
		except:
			quantity = 0
		costPrice.append(quantity)

	totalCostPrice = sum(costPrice)
	try:
		grossProfit = totalSales - totalCostPrice
	except:
		grossProfit = 0

	return {
		"sales":sales,
		"soldItems":soldItems,
		"totalSales":totalSales,
		"totalTax":totalTax,
		'grossProfit': grossProfit,
		'totalCostPrice': totalCostPrice,
		'expenses':expenses
	}

def get_net_profit(year, month=None):
	if year and month:
		sales = sales_period_results(year, month)
		expenses = get_total_expenses(year, month)
	else:
		sales = sales_period_results(year)
		expenses = get_total_expenses(year)

	net = sales['grossProfit'] - expenses['expenses']
	return {
		'net':net
	}
@staff_member_required
def sales_profit(request):
	month = request.GET.get('month')
	year = request.GET.get('year')
	period = request.GET.get('period')
	pdf = request.GET.get('pdf')
	image = request.GET.get('image')
	jax = request.GET.get('ajax')

	if not year:
		year = datetime.datetime.today().year

	if not month:
		month = datetime.datetime.today().month

	try:
		dateperiod = []
		dateresults = []
		epp = None
		totalexpenses = []
		pettycashexpenses = []
		expensesstatus = 0
		netprofit = []
		if year and month:
			if len(str(month)) == 1:
				m = '0' + str(month)
				fdate = str(year) + '-' + m
			else:
				fdate = str(year) + '-' + str(month)
			d = datetime.datetime.strptime(fdate, "%Y-%m")
			ep = []
			epp = []
			if period == 'year':
				p = d - dateutil.relativedelta.relativedelta(years=1)
				tt = sales_period_results(str(p.strftime("%Y")))
				a = {}
				a['totalSales'] = tt['totalSales']
				a['totalTax'] = tt['totalTax']
				a['grossProfit'] = tt['grossProfit']
				a['totalCostPrice'] = tt['totalCostPrice']
				dateperiod.append(str(p.strftime("%Y")))
				dateresults.append(a)

				tt2 = get_total_expenses(str(p.strftime("%Y")))
				pp = get_pettycash_expenses(str(p.strftime("%Y")))
				net = get_net_profit(str(p.strftime("%Y")))
				aa = {}
				bb = {}
				cc = {}
				expensesstatus += pp['expenses']
				aa['expenses'] = tt2['expenses']
				bb['expenses'] = pp['expenses']
				cc['net'] = net['net']
				totalexpenses.append(aa)
				pettycashexpenses.append(bb)
				netprofit.append(cc)

				for n in PersonalExpenses.objects.filter(added_on__year=str(p.strftime("%Y"))):
					ep.append(n.expense_type)

				ep = list(set(ep))

				for i in ep:
					a2 = []
					b2 = {}
					b2['amount'] = \
						PersonalExpenses.objects.filter(added_on__year=str(p.strftime("%Y")),
														expense_type__icontains=str(i)).aggregate(Sum('amount'))[
							'amount__sum']
					a2.append(b2)
					epp.append({'name': i, 'amounts': a2})

			else:
				for i in range(0, 3):
					p = d - dateutil.relativedelta.relativedelta(months=i)
					tt = sales_period_results(year, str(p.strftime("%m")))
					a = {}
					a['totalSales'] = tt['totalSales']
					a['totalTax'] = tt['totalTax']
					a['grossProfit'] = tt['grossProfit']
					a['totalCostPrice'] = tt['totalCostPrice']
					a['sales'] = tt['sales']
					dateperiod.append(p.strftime("%B"))
					dateresults.append(a)

					tt2 = get_total_expenses(year, str(p.strftime("%m")))
					pp = get_pettycash_expenses(year, str(p.strftime("%m")))
					net = get_net_profit(year, str(p.strftime("%m")))
					aa = {}
					bb = {}
					cc = {}
					expensesstatus += pp['expenses']
					aa['expenses'] = tt2['expenses']
					bb['expenses'] = pp['expenses']
					cc['net'] = net['net']
					totalexpenses.append(aa)
					pettycashexpenses.append(bb)
					netprofit.append(cc)

					for n in PersonalExpenses.objects.filter(added_on__year=year,added_on__month=str(p.strftime("%m"))):
						ep.append(n.expense_type)

				ep = list(set(ep))

				for i in ep:
					a2= []
					for pp in range(0, 3):
						p2 = d - dateutil.relativedelta.relativedelta(months=pp)
						b2 = {}
						b2['amount'] = PersonalExpenses.objects.filter(added_on__year=year, added_on__month=str(p2.strftime("%m")),expense_type__icontains = str(i)).aggregate(Sum('amount'))['amount__sum']
						a2.append(b2)
					epp.append({'name': i, 'amounts': a2})

		img = image64()
		startYear = Sales.objects.all().first().created.year
		startMonth = Sales.objects.all().first().created.month


		data = {
			'dateperiod':dateperiod,
			'dateresults':dateresults,
			'epp':epp,
			'netprofit':netprofit,
			'totalexpenses':totalexpenses,
			'pettycashexpenses':pettycashexpenses,
			'expensesstatus':expensesstatus,
			'date':year,
			'status':'true',
			'puller':request.user,
			'image': img,
			'reportImage':image,
			'startYear':startYear,
			'startMonth':startMonth,
			'today':datetime.datetime.now()
		}
		if pdf:
			pdf = render_to_pdf('dashboard/reports/sales_profit/pdf.html', data)
			return HttpResponse(pdf, content_type='application/pdf')
		elif jax:
			return TemplateResponse(request, 'dashboard/reports/sales_profit/ajax.html', data)
		else:
			return TemplateResponse(request, 'dashboard/reports/sales_profit/profit.html', data)
	except Exception, e:
		print (e)
		# return HttpResponse(e)
		data = {
			'status': 'false',
			'date':year
		}
		if jax:
			return TemplateResponse(request, 'dashboard/reports/sales_profit/ajax.html', data)
		else:
			return TemplateResponse(request, 'dashboard/reports/sales_profit/profit.html', data)

@staff_member_required
def sales_tax(request):
	get_date = request.GET.get('date')
	pdf = request.GET.get('pdf')
	image = request.GET.get('image')
	jax = request.GET.get('ajax')

	dateFrom = request.GET.get('dateFrom')
	dateTo = request.GET.get('dateTo')

	today = datetime.datetime.now()
	if get_date:
		date = get_date
		date2 = request.GET.get('date2')
	elif dateFrom and dateTo:
		x = []
		a, b, c = dateFrom.split('-')
		x.append(c)
		x.append(b)
		x.append(a)
		dateFrom2 = '-'.join(x)
		y = []
		d, e, f = dateTo.split('-')
		y.append(f)
		y.append(e)
		y.append(d)
		dateTo2 = '-'.join(y)

		z = []
		g, h, i = dateTo.split('-')
		z.append(g)
		if i == '30':
			z.append(h)
			z.append(str(int(i) + 1))
		elif i =='31':
			z.append(str(int(h) + 1))
			z.append('01')
		else:
			z.append(h)
			z.append(str(int(i) + 1))
		dateTo = '-'.join(z)
		date2 = dateFrom2 + ' - ' + dateTo2
	else:
		try:
			last_sale = Sales.objects.latest('id')
			date = DateFormat(last_sale.created).format('Y-m-d')
			date2 = DateFormat(last_sale.created).format('d/m/Y')
		except:
			date = DateFormat(datetime.datetime.today()).format('Y-m-d')
			date2 = DateFormat(datetime.datetime.today()).format('d/m/Y')

	try:
		if dateFrom and dateTo:
			sales = Sales.objects.filter(created__range=[str(dateFrom), str(dateTo)])
			soldItems = SoldItem.objects.filter(sales__created__range=[str(dateFrom), str(dateTo)]).order_by('-id')
			totalSales = sales.aggregate(Sum('total_net'))['total_net__sum']
			totalSalesTax = sales.aggregate(Sum('total_tax'))['total_tax__sum']
		else:
			sales = Sales.objects.filter(created__icontains=date).order_by('-id')
			soldItems = SoldItem.objects.filter(sales__created__icontains=date).order_by('-id')
			totalSales = sales.aggregate(Sum('total_net'))['total_net__sum']
			totalSalesTax = sales.aggregate(Sum('total_tax'))['total_tax__sum']



		costPrice = []
		for i in soldItems:
			product = ProductVariant.objects.get(sku=i.sku)
			try:
				cost = product.get_cost_price().gross
			except Exception,e:
				cost = product.get_cost_price()
			except Exception,e:
				cost = 0
			costPrice.append(cost)

		totalCost = sum(costPrice)
		if totalCost == 0:
			totalCostTax = 0
		else:
			totalCostTax = round((totalCost-((totalCost*100))/116), 2)
		taxDiff = totalSalesTax - totalCostTax

		img = image64()
		data = {
			'totalCostTax':totalCostTax,
			'totalSalesTax':totalSalesTax,
			'taxDiff':taxDiff,
			'date':date2,
			'status':'true',
			'puller':request.user,
			'image': img,
			'reportImage':image
		}
		if pdf:
			pdf = render_to_pdf('dashboard/reports/sales_tax/pdf.html', data)
			return HttpResponse(pdf, content_type='application/pdf')
		elif jax:
			return TemplateResponse(request, 'dashboard/reports/sales_tax/ajax.html', data)
		else:
			return TemplateResponse(request, 'dashboard/reports/sales_tax/tax.html', data)
	except Exception, e:
		data = {
			'status': 'false',
			'date':date2
		}
		print (e)
		if jax:
			return TemplateResponse(request, 'dashboard/reports/sales_tax/ajax.html', data)
		else:
			return TemplateResponse(request, 'dashboard/reports/sales_tax/tax.html', data)