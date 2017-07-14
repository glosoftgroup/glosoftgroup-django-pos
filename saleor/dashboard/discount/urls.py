from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views

urlpatterns = [
    url(r'sale/$', permission_required('sale.view_sale', login_url='not_found')
        (views.sale_list), name='sale-list'),
    url(r'sale/(?P<pk>[0-9]+)/$', permission_required('sale.edit_sale', login_url='not_found')
        (views.sale_edit), name='sale-update'),
    url(r'sale/(?P<pk>[0-9]+)/detail/$', views.discount_detail, name='discount-detail'),
    url(r'sale/add/$', permission_required('sale.add_sale', login_url='not_found')
        (views.sale_edit), name='sale-add'),
    url(r'sale/(?P<pk>[0-9]+)/delete/$', permission_required('sale.delete_sale', login_url='not_found')
        (views.sale_delete), name='sale-delete'),

    url(r'voucher/$', views.voucher_list, name='voucher-list'),
    url(r'voucher/(?P<pk>[0-9]+)/$', views.voucher_edit, name='voucher-update'),
    url(r'voucher/add/$', views.voucher_edit, name='voucher-add'),
    url(r'voucher/(?P<pk>[0-9]+)/delete/$', views.voucher_delete, name='voucher-delete'),
]
