from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views, accounts
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # paymentoption urls
    url(r'^$', permission_required('banking.view_bank', login_url='account_login')
            (views.list), name='car-list'),
    url(r'^add/$', permission_required('banking.add_bank', login_url='account_login')
            (views.add), name='car-add'),
    url(r'^delete/(?P<pk>[0-9]+)/$', permission_required('banking.delete_bank', login_url='account_login')
            (views.delete), name='car-delete'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.detail, name='car-detail'),
    url(r'^update/(?P<pk>[0-9]+)/$', views.edit, name='update-car'),
    url( r'^search/$', views.searchs, name='car-search'),
    url(r'^paginate/', views.paginate, name='car2_paginate'),

    ]

if settings.DEBUG:
    # urlpatterns += [ url(r'^static/(?P<path>.*)$', serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)