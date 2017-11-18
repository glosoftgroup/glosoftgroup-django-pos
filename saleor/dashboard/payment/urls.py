from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # paymentoption urls
    url(r'^$', permission_required('sale.view_paymentoption', login_url='account_login')
            (views.payments_list), name='payments-list'),
    url(r'^add/$', permission_required('sale.add_paymentoption', login_url='account_login')
            (views.payment_add), name='payment-add'),
    url(r'^delete/(?P<pk>[0-9]+)/$', permission_required('sale.delete_paymentoption', login_url='account_login')
            (views.delete), name='option-delete'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.detail, name='payment-option-detail'),
    url(r'^update/(?P<pk>[0-9]+)/$', views.edit, name='update-payment-option'),
    url(r'^option/search/$', views.option_searchs, name = 'payment-option-search' ),
    url(r'^option/paginate/', views.options_paginate, name='options_paginate'),

    # stock
    url(r'^stock/$',
        permission_required('sale.view_paymentoption', login_url='account_login')
        (views.payments_stock_list), name='payments-stock-list'),
    url(r'^stock/add/$',
        permission_required('sale.add_paymentoption', login_url='account_login')
        (views.payment_stock_add), name='payment-stock-add'),
    url(r'^stock/delete/(?P<pk>[0-9]+)/$', permission_required('sale.delete_paymentoption', login_url='account_login')
        (views.stock_delete), name='option-stock-delete'),
    url(r'^stock/detail/(?P<pk>[0-9]+)/$', views.stock_detail, name='payment-option-stock-detail'),
    url(r'^stock/update/(?P<pk>[0-9]+)/$', views.stock_edit, name='update-payment-stock-option'),
    url(r'^stock/option/search/$', views.option_stock_search, name='payment-option-stock-search'),
    url(r'^stock/option/paginate/', views.options_stock_paginate, name='options_stock_paginate'),

]

if settings.DEBUG:
    # urlpatterns += [ url(r'^static/(?P<path>.*)$', serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)