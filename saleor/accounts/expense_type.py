from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.http import HttpResponse
from ..dashboard.views import staff_member_required
from ..decorators import user_trail
from .models import ExpenseType

from structlog import get_logger

logger = get_logger(__name__)


@staff_member_required
def add(request):
    expense_type = request.POST.get('expense_type')
    option = request.POST.get('option')
    new_expense = ExpenseType(name=expense_type)
    if option:
        try:
            new_expense.save()
            expense_types = ExpenseType.objects.all()
            data = {"expense_types": expense_types}
            return TemplateResponse(request, 'dashboard/sites/hr/select_role.html', data)
        except Exception as e:
            logger.error(e)
            return HttpResponse('error')
    else:
        try:
            new_expense.save()
            expense_types = ExpenseType.objects.all()
            data = {"expense_types": expense_types}
            return TemplateResponse(request, 'dashboard/sites/hr/department.html', data)
        except Exception as e:
            logger.error(e)
            return HttpResponse('error')


def delete(request, pk):
    expense_type = get_object_or_404(ExpenseType, pk=pk)
    if request.method == 'POST':
        expense_type.delete()
        user_trail(request.user.name, 'deleted expense_type: ' + str(expense_type.name), 'delete')
        return HttpResponse('success')


def edit(request, pk):
    expense_type = get_object_or_404(ExpenseType, pk=pk)
    if request.method == 'POST':
        new_expense_type = request.POST.get('department')
        expense_type.name = new_expense_type
        expense_type.save()
        user_trail(request.user.name,
                   'updated expense_type from: ' + str(expense_type.name) + ' to: ' + str(new_expense_type), 'update')
        return HttpResponse('success')
