from django.conf.urls import url

from . import views, expense_type, petty_cash, personal_expenses, expenses_pdf


urlpatterns = [
    url(r'^$', views.expenses, name='expenses'),
	url(r'^add/expense/$', views.add, name='add_expense'),
	url(r'^add/process/$', views.add_process, name='add_expense_process'),
	url(r'^delete/(?P<pk>[0-9]+)/$', views.delete, name='expense-delete'),
	url(r'^expenses/paginate/', views.expenses_paginate, name='expenses_paginate'),
	url( r'^expenses/search/$', views.expenses_search, name = 'expenses_search' ),
	url(r'^detail/(?P<pk>[0-9]+)/$', views.detail, name='pexpense-detail'),

	url(r'^personal/expenses/$', personal_expenses.expenses, name='personal_expenses'),
	url(r'^add/pexpense/$', personal_expenses.add, name='add_personal_expense'),
	url(r'^add/pprocess/$', personal_expenses.add_process, name='add_personal_expense_process'),
	url(r'^pdelete/(?P<pk>[0-9]+)/$', personal_expenses.delete, name='personal-expense-delete'),
	url(r'^p/expenses/paginate/', personal_expenses.expenses_paginate, name='personal_expenses_paginate'),
	url( r'^pexpenses/search/$', personal_expenses.expenses_search, name = 'personal_expenses_search' ),
	url(r'^detail/b/(?P<pk>[0-9]+)/$', personal_expenses.detail, name='bexpense-detail'),
	url( r'^expenses/pdf/$', expenses_pdf.pdf, name ='expenses_pdf'),

	url(r'^add/expense/type/$', expense_type.add, name='add_expense_type'),
	url(r'^pty/cash/$', petty_cash.view, name='petty_cash'),
	url(r'^pty/cash/add/$', petty_cash.add, name='petty_cash_add'),
	url(r'^pty/cash/balance/$', petty_cash.balance, name='petty_cash_balance'),
	url(r'^pty/cash/exp/$', petty_cash.expenditure, name='pettycash_expenditure'),
]
