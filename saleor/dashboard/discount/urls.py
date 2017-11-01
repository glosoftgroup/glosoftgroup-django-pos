from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views

urlpatterns = [
    url(r'sale/$', permission_required('discount.view_voucher', login_url='not_found')
        (views.sale_list), name='sale-list'),
    url(r'discount/paginate/$', views.disc_paginate, name='discount_pagination'),
    url(r'discount/search/$', views.disc_search, name='discount_search'),
    url(r'sale/(?P<pk>[0-9]+)/$', permission_required('sale.edit_sale', login_url='not_found')
        (views.sale_edit), name='sale-update'),
    url(r'disc/det/paginate/$', views.disc_products_paginate, name='disc_products_paginate'),
    url(r'disc/det/search/$', views.disc_products_search, name='disc_products_search'),
    url(r'sale/(?P<pk>[0-9]+)/detail/$', views.discount_detail, name='discount-detail'),
    url(r'sale/add/$', permission_required('discount.add_voucher', login_url='not_found')
        (views.sale_edit), name='sale-add'),
    url(r'sale/(?P<pk>[0-9]+)/delete/$', permission_required('discount.delete_voucher', login_url='not_found')
        (views.sale_delete), name='sale-delete'),

    url(r'token/search/variants/$', permission_required('discount.add_voucher', login_url='not_found')
        (views.token_variants), name='token-search-variants'),
    url(r'add/discount/data/$', permission_required('discount.add_voucher', login_url='not_found')
        (views.create_discount), name='create-discount'),
    

    url(r'voucher/$', views.voucher_list, name='voucher-list'),
    url(r'voucher/(?P<pk>[0-9]+)/$', views.voucher_edit, name='voucher-update'),
    url(r'voucher/add/$', views.voucher_edit, name='voucher-add'),
    url(r'voucher/(?P<pk>[0-9]+)/delete/$', views.voucher_delete, name='voucher-delete'),

    
]
