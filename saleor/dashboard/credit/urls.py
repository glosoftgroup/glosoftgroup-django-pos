from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views,charts, pdfs,  purchase, sales_margin, sales_tax, sales_margin2
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
		url(r'^$', permission_required('reports.view_sales_reports', login_url='not_found')
<<<<<<< HEAD
			(views.credit_reports), name='credit_reports'),
		url(r'^credit/$', permission_required('reports.view_sales_reports', login_url='not_found')
			(views.credit_list), name='credit_list'),
=======
			(views.credit_list), name='credit_list'),
		url(r'^credit/$', permission_required('reports.view_sales_reports', login_url='not_found')
			(views.credit_reports), name='credit_reports'),
>>>>>>> a82994a10f39d2d0929cf9084d45039380aed711
		url(r'^detail/(?P<pk>[0-9]+)/$', permission_required('reports.view_sales_reports', login_url='not_found')
			(views.credit_detail), name='credit-detail'),

		url( r'^credit_search/$', views.credit_search, name = 'credit_search' ),
		url( r'^credit_paginate/$', views.credit_paginate, name = 'credit_paginate'),
		

		url(r'^reports/sales/list/pdf/$', pdfs.sales_list_pdf, name='reports_credit_list_pdf'),
		
		url( r'^sales/margin/$', sales_margin.sales_margin, name = 'credit_margin' ),
		url( r'^sales/tax/report/$', sales_margin.sales_tax, name = 'credit_tax' ),

]

if settings.DEBUG:
	# urlpatterns += [ url(r'^static/(?P<path>.*)$', serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)