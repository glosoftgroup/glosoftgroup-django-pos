from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views, sales
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
        url(r'^$', permission_required('customer.view_customer', login_url='account_login')
            (views.users), name='customers'),
        url(r'^add/$', permission_required('customer.add_customer', login_url='account_login')
            (views.user_add), name='customer-add'),
        url(r'^customer_process/$', views.user_process, name='customer_process'),
        url(r'^d/(?P<pk>[0-9]+)/$', views.user_detail, name='customer-detail'),
        url(r'^sd/(?P<pk>[0-9]+)/$', views.sales_detail, name='customer-sales-detail'),
        url(r'^cst/pdf/detail/(?P<pk>[0-9]+)/$', sales.sales_detail, name='cust-pdf-sale-detail'),
        url(r'^std/(?P<pk>[0-9]+)/(?P<ck>[0-9]+)/$', views.sales_items_detail, name='customer-sales-items-detail'),
        url(r'^delete/(?P<pk>[0-9]+)/$', permission_required('customer.delete_customer', login_url='account_login')
            (views.user_delete), name='customer-delete'),
        url(r'^edit/(?P<pk>[0-9]+)/$', permission_required('customer.change_customer', login_url='account_login')
            (views.user_edit), name='customer-edit'),
        url(r'^user_update(?P<pk>[0-9]+)/$', views.user_update, name='customer-update'),
        url(r'^customer/paginate/$', views.customer_pagination, name='customer-paginate'),
        url(r'^customer/search/$', views.customer_search, name='customer-search'),

        url( r'^customer/sales/paginate/customer-sales-detail$', sales.sales_paginate, name = 'customer_sales_paginate'),
        url( r'^customer/sales/search/$', sales.sales_search, name = 'customer_sales_search'),
        url(r'^customer/sales/list/pdf/$', sales.sales_list_pdf, name='customers_sales_list_pdf'),

        url( r'^customer/canbe/creditable/$', views.is_creditable, name = 'is_creditable'),

        # reports urls
        url(r'^reports/$', permission_required('customer.view_customer', login_url='not_found')
            (views.customer_report), name='customer_report_list'),        
        url(r'^report/paginate/$', views.report_pagination, name='customer-report-paginate'),
        url(r'^report/search/$', views.report_search, name='customer-report-search'),

        # credit urls        
        url(r'^credit-list/$', permission_required('customer.view_customer', login_url='not_found')
            (views.credit_report), name='customer_credit_list'),        
        url(r'^credit/paginate/$', views.credit_pagination, name='customer-credit-paginate'),
        url(r'^credit/search/$', views.credit_search, name='customer-credit-search'),


        
]

if settings.DEBUG:    
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)