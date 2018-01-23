from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
        # car reports
        url(r'^$', permission_required('reports.view_sale_reports', login_url='not_found')
            (views.allocate_list), name='sale_purchase_list'),
        url(r'^transfer/(?P<pk>[0-9]+)/$', permission_required('reports.view_sale_reports', login_url='not_found')
            (views.single_list), name='sale_supplier_list'),
        url(r'^transfer/detail/(?P<pk>[0-9]+)/$', permission_required('reports.view_sale_reports', login_url='not_found')
            (views.allocate_detail), name='sale-purchase-detail'),

        # product purchase
        url(r'^product/$', permission_required('reports.view_sale_reports', login_url='not_found')
            (views.purchase), name='purchase-product'),

        # product varaint purchase reports
        url(r'^report/$', permission_required('reports.view_sale_reports', login_url='not_found')
            (views.report_list), name='purchase-variant'),
        url(r'^report/(?P<pk>[0-9]+)/$', permission_required('reports.view_sale_reports', login_url='not_found')
            (views.report_single), name='purchase-variant-single'),
        url(r'^report/(?P<pk>[0-9]+)/detail/$', permission_required('reports.view_sale_reports', login_url='not_found')
            (views.report_detail), name='purchase-variant-detail'),
        url(r'^report/update/(?P<pk>[0-9]+)/detail/$', permission_required('reports.view_sale_reports', login_url='not_found')
            (views.update_detail), name='purchase-variant-update'),


]

if settings.DEBUG:	
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)