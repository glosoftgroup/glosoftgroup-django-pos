from django.conf.urls import url

from . import views, expense_type


urlpatterns = [
    url(r'^$', views.expenses, name='expenses'),
	url(r'^add/expense/$', views.add, name='add_expense'),
	url(r'^add/process/$', views.add_process, name='add_expense_process'),
	url(r'^delete/(?P<pk>[0-9]+)/$', views.delete, name='expense-delete'),
	url(r'^expenses/paginate/', views.expenses_paginate, name='expenses_paginate'),
	url( r'^expenses/search/$', views.expenses_search, name = 'expenses_search' ),

	url(r'^add/expense/type$', expense_type.add, name='add_expense_type'),
]
