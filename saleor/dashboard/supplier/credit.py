import logging
from django.template.response import TemplateResponse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.db.models import Count, Min, Sum, Avg, F, Q
from ..views import staff_member_required
from ...purchase.models import PurchaseProduct
from ...decorators import permission_decorator, user_trail
from ...credit.models import Credit, CreditedItem, CreditHistoryEntry
from ...utils import render_to_pdf, default_logo
from django.utils.dateformat import DateFormat
from datetime import date, datetime

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


@staff_member_required
@permission_decorator('supplier.view_supplier')
def credit_report(request):
    try:
        users = PurchaseProduct.objects.filter(~Q(payment_options__name='credit')).order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(users, 10)
        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except InvalidPage:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
        user_trail(request.user.name, 'accessed suppliers page', 'view')
        info_logger.info('User: ' + str(request.user.name) + 'view suppliers')
        return TemplateResponse(request, 'dashboard/supplier/credit/list.html',{'users': users, 'pn': paginator.num_pages})
    except TypeError as e:
		print ('dsd')
		print e
		print ('dsd')
		error_logger.error(e)
		return TemplateResponse(request, 'dashboard/supplier/credit/list.html', {})


@staff_member_required
def credit_search(request):
    if request.is_ajax():
		page = request.GET.get('page', 1)
		list_sz = request.GET.get('size', 10)
		p2_sz = request.GET.get('psize')
		q = request.GET.get('q')
		if list_sz == 0:
			sz = 10
		else:
			sz = list_sz
		if q is not None:
			queryset_list = PurchaseProduct.objects.filter(~Q(payment_options__name='credit')).filter(
				Q(supplier__name__icontains=q)|
				Q(supplier__email__icontains=q) |
				Q(supplier__mobile__icontains=q)
			).order_by('-id')

			if list_sz:
				paginator = Paginator(queryset_list, int(list_sz))
				users = paginator.page(page)
				return TemplateResponse(request, 'dashboard/supplier/credit/pagination/credit_search.html',
										{'users': users, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0, 'q': q})

			if p2_sz:
				paginator = Paginator(queryset_list, int(p2_sz))
				users = paginator.page(page)
				return TemplateResponse(request, 'dashboard/supplier/credit/pagination/credit_paginate.html',
								{"users": users})
			paginator = Paginator(queryset_list, 10)

			try:
				queryset_list = paginator.page(page)
			except PageNotAnInteger:
				queryset_list = paginator.page(1)
			except InvalidPage:
				queryset_list = paginator.page(1)
			except EmptyPage:
				queryset_list = paginator.page(paginator.num_pages)
			users = queryset_list

			return TemplateResponse(request, 'dashboard/supplier/credit/pagination/credit_search.html',
			{"users":users, 'pn': paginator.num_pages, 'sz': sz, 'q': q})


@staff_member_required
def credit_pagination(request):
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')

    users = PurchaseProduct.objects.filter(~Q(payment_options__name='credit')).order_by('-id').order_by('-id')
    if list_sz:
        paginator = Paginator(users, int(list_sz))
        users = paginator.page(page)
        return TemplateResponse(request, 'dashboard/supplier/credit/pagination/credit_p2.html',
                                {'users':users, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0})
    else:
        paginator = Paginator(users, 10)
    if p2_sz:
        paginator = Paginator(users, int(p2_sz))
        users = paginator.page(page)
        return TemplateResponse(request, 'dashboard/supplier/credit/pagination/credit_paginate.html', {"users":users})

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except InvalidPage:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    return TemplateResponse(request, 'dashboard/supplier/credit/pagination/credit_paginate.html', {"users":users})

@staff_member_required
@permission_decorator('reports.view_sale_reports')
def credit_history(request, credit_pk=None):
	if credit_pk:
		credit = PurchaseProduct.objects.get(pk=credit_pk)
		total_amount = credit.total_cost
		total_balance = credit.total_cost - credit.amount_paid
	else:
		credit = PurchaseProduct()
	try:
		try:
			last_sale = PurchaseProduct.objects.latest('id')
			last_date_of_sales = DateFormat(last_sale.created).format('Y-m-d')
		except:
			last_date_of_sales = DateFormat(datetime.today()).format('Y-m-d')

		all_sales = credit.total_cost
		total_sales_amount = 0 #all_sales.aggregate(Sum('total_net'))
		total_tax_amount = 0 #all_sales.aggregate(Sum('total_tax'))
		total_sales = []


		page = request.GET.get('page', 1)
		paginator = Paginator(total_sales, 10)
		try:
			total_sales = paginator.page(page)
		except PageNotAnInteger:
			total_sales = paginator.page(1)
		except InvalidPage:
			total_sales = paginator.page(1)
		except EmptyPage:
			total_sales = paginator.page(paginator.num_pages)
		user_trail(request.user.name, 'accessed credit sales reports', 'view')
		info_logger.info('User: ' + str(request.user.name) + ' accessed the view credit sales report page')
		ctx = {
			   'pn': paginator.num_pages,
			   'sales': all_sales,
			   "credit":credit,
			   'total_amount':total_amount,
			   'total_balance':total_balance,
			   "total_sales_amount":total_sales_amount,
			   "total_tax_amount":total_tax_amount,
			   "date":last_date_of_sales
			   }
		return TemplateResponse(request, 'dashboard/supplier/credit/history.html',ctx)
	except ObjectDoesNotExist as e:
		error_logger.error(e)
		return HttpResponse('Error matching query')


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def credit_detail_pdf(request, pk=None):
	try:
		credit = Credit.objects.get(pk=pk)
		all_sales = CreditHistoryEntry.objects.filter(credit=credit)
		img = default_logo()
		data = {
			'today': date.today(),
			'sales': all_sales,
			'credit': credit,
			'puller': request.user,
			'image': img
		}
		pdf = render_to_pdf('dashboard/supplier/credit/pdf/pdf.html',data)
		return HttpResponse(pdf, content_type='application/pdf')
	except ObjectDoesNotExist as e:
		error_logger.error(e)
		return HttpResponse(e)