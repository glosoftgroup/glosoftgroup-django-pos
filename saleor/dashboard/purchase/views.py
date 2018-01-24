from django.core.exceptions import ObjectDoesNotExist
from django.template.response import TemplateResponse
from django.http import HttpResponse, JsonResponse
import logging
import json
from decimal import Decimal

from ..views import staff_member_required
from ...purchase.models import PurchaseProduct as Table
from ...purchase.models import PurchaseVariant
from ...purchase.models import PurchasedItem as Item
from ...purchase.models import PurchaseVariantHistoryEntry as History
from ...decorators import permission_decorator
from ...supplier.models import Supplier
from saleor.payment.models import PaymentOption

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')
table_name = 'Purchases'


@staff_member_required
@permission_decorator('reports.view_sale_reports')
def allocate_list(request):
    global table_name
    data = {
        "table_name": table_name,
    }
    return TemplateResponse(request, 'dashboard/reports/' + table_name.lower() + '/list.html', data)


@staff_member_required
@permission_decorator('reports.view_sale_reports')
def single_list(request, pk=None):
    global table_name
    if not pk:
        return HttpResponse(table_name+' pk required')
    name = ''
    try:
        name = Table.objects.get(pk=pk).supplier.name
    except Exception as e:
        pass
    data = {
        "table_name": table_name,
        "pk": pk,
        "name": name
    }
    return TemplateResponse(request, 'dashboard/reports/' + table_name.lower() + '/more.html', data)


@staff_member_required
@permission_decorator('reports.view_sale_reports')
def allocate_detail(request, pk=None):
    try:
        sale = Table.objects.get(pk=pk)
        items = {} #AllocatedItem.objects.filter(allocate=sale)
        return TemplateResponse(request, 'dashboard/reports/car/details.html', {'items': items, "sale": sale})
    except ObjectDoesNotExist as e:
        error_logger.error(e)
        return HttpResponse('No items found')


# purchase product
# purchase form
@staff_member_required
@permission_decorator('reports.view_sale_reports')
def purchase(request):
    global table_name
    suppliers = Supplier.objects.all()
    payment_options = PaymentOption.objects.all()
    data = {
        "table_name": table_name,
        'suppliers': suppliers,
        'payment_options': payment_options
    }
    return TemplateResponse(request, 'dashboard/purchase/form.html', data)


# report
@staff_member_required
@permission_decorator('reports.view_sale_reports')
def report_list(request):
    global table_name
    data = {
        "table_name": table_name,
    }
    return TemplateResponse(request, 'dashboard/purchase/reports/list.html', data)


@staff_member_required
@permission_decorator('reports.view_sale_reports')
def report_single(request, pk=None):
    global table_name
    if not pk:
        return HttpResponse(table_name+' pk required')
    name = ''
    try:
        name = PurchaseVariant.objects.get(pk=pk).supplier.name
    except Exception as e:
        pass
    data = {
        "table_name": table_name,
        "pk": pk,
        "name": name
    }
    return TemplateResponse(request, 'dashboard/purchase/reports/more.html', data)


@staff_member_required
@permission_decorator('reports.view_sale_reports')
def report_detail(request, pk=None):
    try:
        sale = PurchaseVariant.objects.get(pk=pk)
        items = Item.objects.filter(purchase=sale)
        history = History.objects.filter(purchase=sale)
        return TemplateResponse(request, 'dashboard/purchase/reports/details.html',{'items': items, "sale":sale, 'history':history})
    except ObjectDoesNotExist as e:
        error_logger.error(e)


@staff_member_required
@permission_decorator('reports.view_sale_reports')
def update_detail(request, pk=None):
    if request.method == "POST":
        if pk:
            sale = PurchaseVariant.objects.get(pk=pk)
        else:
            return HttpResponse('PK required')
        if request.POST.get('history'):
            items = json.loads(request.POST.get('history'))
            for item in items:
                history = History()
                history.purchase = sale
                history.tendered = item['tendered']
                history.transaction_number = item['transaction_number']
                history.payment_name = item['payment_name']
                history.save()
                sale.amount_paid += Decimal(item['tendered'])
                sale.balance -= Decimal(item['tendered'])
            print sale.amount_paid
            print sale.total_net
            if sale.amount_paid < sale.total_net:
                # credit sale
                sale.status = 'payment-pending'
            else:
                sale.status = 'fully-paid'
                sale.amount_paid = sale.total_net
                sale.balance = 0
            sale.save()
            result = json.dumps({'results':{
                                        'amount_paid': str(sale.amount_paid),
                                        'balance': str(sale.balance)
                                      }
                                 })
            return HttpResponse(result)
        return HttpResponse('payment history expected')
    return HttpResponse('Invalid method')
