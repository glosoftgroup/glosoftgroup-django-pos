from django.core.exceptions import ObjectDoesNotExist
from django.template.response import TemplateResponse
from django.http import HttpResponse, JsonResponse
import logging

from ..views import staff_member_required
from ...purchase.models import PurchaseProduct as Table
from ...decorators import permission_decorator

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

