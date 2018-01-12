from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views,charts, car, pdfs,  purchase, sales_margin, sales_tax, sales_margin2
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
        url(r'^$', permission_required('reports.view_sale_reports', login_url='not_found')
            (views.allocate_list), name='allocate_list'),
        url(r'^history/(?P<credit_pk>[0-9]+)/$', permission_required('reports.view_sale_reports', login_url='not_found')
            (views.allocate_history), name='credit_history'),
        url(r'^history/pdf/(?P<pk>[0-9]+)/$', permission_required('reports.view_sale_reports', login_url='not_found')
            (views.allocate_detail_pdf), name='allocate_history_pdf'),
        url(r'^allocate/$', permission_required('reports.view_sale_reports', login_url='not_found')
            (views.allocate_reports), name='allocate_reports'),
        url(r'^detail/(?P<pk>[0-9]+)/$', permission_required('reports.view_sale_reports', login_url='not_found')
            (views.allocate_detail), name='allocate-detail'),

        url( r'^allocate_search/$', views.allocate_search, name = 'allocate_search' ),
        url( r'^allocate_paginate/$', views.allocate_paginate, name = 'allocate_paginate'),


        url(r'^reports/credit/list/pdf/$', pdfs.sales_list_pdf, name='reports_allocate_list_pdf'),

        url(r'^reports/credit/category/pdf/$', pdfs.sales_category, name='reports_credit_category_pdf'),
        url(r'^reports/credit/items/pdf/$', pdfs.sales_items, name='reports_credit_items_pdf'),
        url(r'^reports/credit/user/pdf/$', pdfs.sales_user, name='reports_credit_user_pdf'),
        url(r'^reports/credit/till/pdf/$', pdfs.sales_tills, name='reports_credit_tills_pdf'),
        url(r'^pdf/credit/detail/(?P<pk>[0-9]+)/$', permission_required('reports.view_credit_reports', login_url='not_found')
            (pdfs.sales_detail), name='pdf-allocate-detail'),
        url(r'^reports/sales/list/export_csv/$', views.sales_list_export_csv, name='reports_credit_list_export_csv'),


        url(r'^sales/margin/$', sales_margin.sales_margin, name = 'credit_margin' ),
        url(r'^sales/tax/report/$', sales_margin.sales_tax, name = 'credit_tax' ),
        url(r'^credit/sale/notifier/$', views.due_credit_notifier, name = 'due_credit_notifier' ),

        # car reports
        url(r'^car/$', permission_required('reports.view_sale_reports', login_url='not_found')
            (car.allocate_list), name='car_allocate_list'),
        url(r'^car/transfer/(?P<pk>[0-9]+)/$', permission_required('reports.view_sale_reports', login_url='not_found')
            (car.car_list), name='car_transfer_list'),
        url(r'^car/transfer/detail/(?P<pk>[0-9]+)/$', permission_required('reports.view_sale_reports', login_url='not_found')
            (car.allocate_detail), name='car-allocate-detail')

]

if settings.DEBUG:	
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)