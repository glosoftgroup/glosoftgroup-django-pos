from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views, accounts
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # paymentoption urls
    url(r'^$', permission_required('banking.view_bank', login_url='account_login')
            (views.list), name='bank-list'),
    url(r'^add/$', permission_required('banking.add_bank', login_url='account_login')
            (views.add), name='bank-add'),
    url(r'^delete/(?P<pk>[0-9]+)/$', permission_required('banking.delete_bank', login_url='account_login')
            (views.delete), name='bank2-delete'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.detail, name='bank-detail'),
    url(r'^update/(?P<pk>[0-9]+)/$', views.edit, name='update-bank'),
    url( r'^search/$', views.searchs, name='bank-search'),
    url(r'^paginate/', views.paginate, name='bank2_paginate'),

    # accounts
    url(r'^accounts/$', permission_required('banking.view_account', login_url='account_login')
            (accounts.list), name='accounts-list'),
    url(r'^accounts/add/$', permission_required('banking.add_account', login_url='account_login')
            (accounts.add), name='accounts-add'),
    url(r'^accounts/delete/(?P<pk>[0-9]+)/$', permission_required('banking.delete_account', login_url='account_login')
            (accounts.delete), name='accounts-delete'),
    url(r'^accounts/detail/(?P<pk>[0-9]+)/$', accounts.detail, name='accounts-detail'),
    url(r'^accounts/update/(?P<pk>[0-9]+)/$', accounts.edit, name='accounts-bank'),
    url( r'^acounts/search/$', accounts.searchs, name='accounts-search'),
    url(r'^accounts/paginate/', accounts.paginate, name='accounts_paginate'),
    
    ]

if settings.DEBUG:
    # urlpatterns += [ url(r'^static/(?P<path>.*)$', serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)