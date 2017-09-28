from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views,charts, pdfs,  purchase, sales_margin, sales_tax, sales_margin2, product_sales
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
		url(r'^$', permission_required('reports.view_sale_reports', login_url='not_found')
			(views.sales_reports), name='sales_reports'),
		url(r'^sales/$', permission_required('reports.view_sale_reports', login_url='not_found')
			(views.sales_list), name='sales_list'),
		url(r'^prs/sales/$', permission_required('reports.view_sale_reports', login_url='not_found')
			(product_sales.sales_list), name='product_sales_list'),
		url( r'^sales/prs/paginate/$', product_sales.sales_paginate, name = 'product_sales_paginate'),
		url( r'^sales/prs/search/$', product_sales.sales_search, name = 'product_sales_search' ),
		url( r'^sales/prs/pdf/$', product_sales.sales_list_pdf, name = 'product_sales_list_pdf' ),
		url(r'^detail/(?P<pk>[0-9]+)/$', permission_required('reports.view_sale_reports', login_url='not_found')
			(views.sales_detail), name='sale-detail'),

		# Sales Tax
		url(r'^tx/$', permission_required('reports.view_sale_reports', login_url='not_found')
			(sales_tax.sales_reports), name='sales_tax_reports'),
		url(r'^tx/sales/$', permission_required('reports.view_sale_reports', login_url='not_found')
			(sales_tax.sales_list), name='sales_tax_list'),
		url(r'^tx/detail/(?P<pk>[0-9]+)/$', permission_required('reports.view_sale_reports', login_url='not_found')
			(sales_tax.sales_detail), name='sale_tax_detail'),
		url( r'^tx/sales_search/$', sales_tax.sales_search, name = 'sales_tax_search' ),
		url( r'^tx/sales_paginate/$', sales_tax.sales_paginate, name = 'sales_tax_paginate'),
		url(r'^tx/pdf/detail/(?P<pk>[0-9]+)/$', permission_required('reports.view_sale_reports', login_url='not_found')
			(sales_tax.pdf_sale_tax_detail), name='pdf-sale-tax-detail'),
		url(r'^tx/reports/sales/list/pdf/$', sales_tax.sales_list_tax_pdf, name='reports_sales_tax_list_pdf'),

		# Sales Margin
		url(r'^mrg/$', permission_required('reports.view_sale_reports', login_url='not_found')
			(sales_margin2.sales_reports), name='sales_margin_list_reports'),
		url(r'^mrg/sales/$', permission_required('reports.view_sale_reports', login_url='not_found')
			(sales_margin2.sales_list), name='sales_margin_list'),
		url(r'^mrg/detail/(?P<pk>[0-9]+)/$', permission_required('reports.view_sale_reports', login_url='not_found')
			(sales_margin2.sales_detail), name='sale_margin_detail'),
		url( r'^mrg/sales_search/$', sales_margin2.sales_search, name = 'sales_margin_search' ),
		url( r'^mrg/sales_paginate/$', sales_margin2.sales_paginate, name = 'sales_margin_paginate'),
		url(r'^mrg/pdf/detail/(?P<pk>[0-9]+)/$', permission_required('reports.view_sale_reports', login_url='not_found')
			(sales_margin2.pdf_sale_tax_detail), name='pdf-sale-margin-detail'),
		url(r'^mrg/sales/list/pdf/$', sales_margin2.sales_list_tax_pdf, name='reports_sales_margin_list_pdf'),

		url(r'^mrg/sls/itms/paginate/$', sales_margin2.sales_items_paginate, name='sales_margin_items_paginate'),
		url(r'^mrg/sls/itms/search/$', sales_margin2.sales_items_search, name='sales_margin_items_search'),
		url(r'^mrg/sales/list/items/pdf/$', sales_margin2.sales_list_margin_items_pdf, name='reports_sales_margin_items_pdf'),



		url(r'^reports/sales/list/pdf/$', pdfs.sales_list_pdf, name='reports_sales_list_pdf'),
		url(r'^reports/category/pdf/$', pdfs.sales_category, name='reports_sales_category_pdf'),
		url(r'^reports/items/pdf/$', pdfs.sales_items, name='reports_sales_items_pdf'),
		url(r'^reports/discount/pdf/$', pdfs.discount_items, name='reports_discount_items_pdf'),
		url(r'^reports/user/pdf/$', pdfs.sales_user, name='reports_sales_user_pdf'),
		url(r'^reports/till/pdf/$', pdfs.sales_tills, name='reports_sales_tills_pdf'),
		url(r'^pdf/detail/(?P<pk>[0-9]+)/$', permission_required('reports.view_sale_reports', login_url='not_found')
			(pdfs.sales_detail), name='pdf-sale-detail'),
    	url(r'^reports/sales/list/export_csv/$', views.sales_list_export_csv, name='reports_sales_list_export_csv'),

		url(r'^product/$',  permission_required('reports.view_products_reports', login_url='not_found')
			(views.product_reports), name='products_reports'),
		url( r'^product/search/$', views.products_search, name = 'products_search' ),
		url( r'^products/paginate/$', views.products_paginate, name = 'products_paginate' ),
		url(r'^prd/$',  permission_required('reports.view_products_reports', login_url='not_found')
			(views.product_reorder), name='products_reorder'),
		url( r'^prs/$', views.products_reorder_search, name = 'products_reorder_search' ),
		url( r'^prp/$', views.products_reorder_paginate, name = 'products_reorder_paginate' ),
		url(r'^reports/prs/pdf/$', views.reorder_pdf, name='reports_reorder_pdf'),
    	url(r'^reports/prs/export_csv/$', views.reorder_export_csv, name='reports_reorder_export_csv'),
		url(r'^reports/products/pdf/$', views.products_pdf, name='reports_products_pdf'),
    	url(r'^reports/products/export_csv/$', views.products_export_csv, name='reports_products_export_csv'),

		url(r'^purchases/$',  permission_required('reports.view_purchase_reports', login_url='not_found')
			(purchase.purchase_reports), name='purchases_reports'),
		url(r'^purchases/paginate$',  purchase.purchase_paginate, name='purchase_reports_paginate'),
		url(r'^purchases/search$',  purchase.purchase_search, name='purchase_reports_search'),
		url(r'^reports/purchases/pdf/$', purchase.purchase_pdf, name='reports_purchase_pdf'),
    	url(r'^reports/purchases/export_csv/$', purchase.purchase_export_csv, name='reports_purchases_export_csv'),


		url(r'^balancesheet_reports/$', permission_required('reports.view_balancesheet', login_url='not_found')
			(views.balancesheet_reports), name='balancesheet_reports'),
		url(r'^chart/$', views.get_dashboard_data, name='chart'), 
		url( r'^sales_search/$', views.sales_search, name = 'sales_search' ),
		url( r'^sales_paginate/$', views.sales_paginate, name = 'sales_paginate'),
		url(r'^cpdf/(?P<image>.+)/$', pdfs.chart_pdf, name='chart_pdf'),
		url(r'^csv/(?P<image>.+)/$', pdfs.sales_export_csv, name='chart_csv'),

		url( r'^datechart/$',  permission_required('reports.view_sale_reports', login_url='not_found')
			(charts.sales_date_chart), name = 'sales_date_chart' ),
		url( r'^datechartimage/(?P<image>.+)/$', charts.sales_date_chart, name = 'sales_date_chart' ),
		url( r'^productchart/$',  permission_required('reports.view_products_reports', login_url='not_found')
			(charts.sales_product_chart), name = 'sales_product_chart' ),
	    url( r'^productchart/pnt/$',  permission_required('reports.view_products_reports', login_url='not_found')
			(charts.sales_product_chart_paginate), name = 'sales_product_chart_paginate' ),
	    url( r'^discountchart/$',  permission_required('reports.view_products_reports', login_url='not_found')
			(charts.sales_discount_chart), name = 'sales_discount_chart' ),
	    url( r'^discountchart/pnt/$',  permission_required('reports.view_products_reports', login_url='not_found')
			(charts.sales_discount_chart_paginate), name = 'sales_discount_chart_paginate' ),
		
		url( r'^ptd/$', charts.get_product_sale_details, name = 'get_product_sale_details' ),

		url( r'^category/$',  permission_required('reports.view_sale_reports', login_url='not_found')
			(charts.sales_category_chart), name = 'sales_category_chart' ),
		url( r'^category/pnt/$',  permission_required('reports.view_sale_reports', login_url='not_found')
			(charts.sales_category_chart_paginate), name = 'sales_category_chart_paginate' ),
		url( r'^catimage/(?P<image>.+)/$', charts.sales_category_chart, name = 'sales_category_chart' ),
		url( r'^catd/$', charts.get_category_sale_details, name = 'get_category_sale_details' ),
		url( r'^userchart/$',  permission_required('reports.view_sale_reports', login_url='not_found')
			(charts.sales_user_chart), name = 'sales_user_chart' ),
		url( r'user/tchart/pnt/$',  permission_required('reports.view_products_reports', login_url='not_found')
			(charts.sales_user_chart_paginate), name = 'sales_user_chart_paginate' ),
		url( r'^utd/$', charts.get_user_sale_details, name = 'get_user_sale_details' ),
		url( r'^till/chart/$',  permission_required('reports.view_sale_reports', login_url='not_found')
			(charts.sales_terminal_chart), name = 'sales_terminal_chart' ),
		url( r'^till/tchart/pnt/$',  permission_required('reports.view_products_reports', login_url='not_found')
			(charts.sales_till_chart_paginate), name = 'sales_till_chart_paginate' ),
		url( r'^ttd/$', charts.get_terminal_sale_details, name = 'get_terminal_sale_details' ),
		url( r'^weekfilter/$', charts.get_sales_by_week, name = 'get_sales_by_week' ),

		url( r'^sales/margin/$', sales_margin.sales_margin, name = 'sales_margin' ),
		url( r'^sales/tax/report/$', sales_margin.sales_tax, name = 'sales_tax' ),

]

if settings.DEBUG:
	# urlpatterns += [ url(r'^static/(?P<path>.*)$', serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)