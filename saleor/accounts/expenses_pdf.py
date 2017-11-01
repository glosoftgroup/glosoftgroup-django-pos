from django.db.models import Q
from django.http import HttpResponse
from .views import staff_member_required
from ..utils import render_to_pdf, default_logo
from datetime import date
from .models import ExpenseType, Expenses, PersonalExpenses


@staff_member_required
def pdf(request):

	if request.is_ajax():
		q = request.GET.get( 'q' )
		gid = request.GET.get('gid')

		type = None
		if q is not None:
			expenses = Expenses.objects.filter(
				Q(expense_type__icontains=q) |
				Q(paid_to__icontains=q) | Q(authorized_by__icontains=q)).order_by('id')

			if gid:
				type = ExpenseType.objects.get(pk=request.GET.get('gid'))
				expenses = expenses.filter(expense_type=type.name)

		elif gid:
			type = ExpenseType.objects.get(pk=request.GET.get('gid'))
			expenses = Expenses.objects.filter(expense_type=type.name)
		else:
			expenses = Expenses.objects.all()
		img = default_logo()
		data = {
			'today': date.today(),
			'expenses': expenses,
			'puller': request.user,
			'image': img,
			'type':type
		}
		pdf = render_to_pdf('dashboard/accounts/expenses/pdf/expenses.html', data)
		return HttpResponse(pdf, content_type='application/pdf')

@staff_member_required
def bpdf(request):

	if request.is_ajax():
		q = request.GET.get( 'q' )
		gid = request.GET.get('gid')

		type = None
		if q is not None:
			expenses = PersonalExpenses.objects.filter(
				Q(expense_type__icontains=q) |
				Q(paid_to__icontains=q) | Q(authorized_by__icontains=q)).order_by('id')

			if gid:
				type = ExpenseType.objects.get(pk=request.GET.get('gid'))
				expenses = expenses.filter(expense_type=type.name)

		elif gid:
			type = ExpenseType.objects.get(pk=request.GET.get('gid'))
			expenses = PersonalExpenses.objects.filter(expense_type=type.name)
		else:
			expenses = PersonalExpenses.objects.all()
		img = default_logo()
		data = {
			'today': date.today(),
			'expenses': expenses,
			'puller': request.user,
			'image': img,
			'type':type
		}
		pdf = render_to_pdf('dashboard/accounts/personal_expenses/pdf/pdf.html', data)
		return HttpResponse(pdf, content_type='application/pdf')

