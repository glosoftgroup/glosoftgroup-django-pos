from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # paymentoption urls
    url(r'^$', permission_required('sale.view_table', login_url='account_login')
            (views.list), name='bank-list'),
    url(r'^add/$', permission_required('sale.add_paymentoption', login_url='account_login')
            (views.add), name='bank-add'),
    url(r'^delete/(?P<pk>[0-9]+)/$', permission_required('sale.delete_paymentoption', login_url='account_login')
            (views.delete), name='bank2-delete'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.detail, name='bank-detail'),
    url(r'^update/(?P<pk>[0-9]+)/$', views.edit, name='update-bank'),
    url( r'^search/$', views.searchs, name='bank-search'),
    url(r'^paginate/', views.paginate, name='bank2_paginate'),
    
    ]

if settings.DEBUG:
    # urlpatterns += [ url(r'^static/(?P<path>.*)$', serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)