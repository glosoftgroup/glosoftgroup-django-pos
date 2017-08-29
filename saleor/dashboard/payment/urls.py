from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # paymentoption urls
    url(r'^$', views.payments_list, name='payments-list'),       
    url(r'^add/$', views.payment_add, name='payment-add'),       
    url(r'^delete/(?P<pk>[0-9]+)/$', views.delete, name='option-delete'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.detail, name='payment-option-detail'),
    url(r'^update/(?P<pk>[0-9]+)/$', views.edit, name='update-payment-option'),
    url( r'^option/search/$', views.option_searchs, name = 'payment-option-search' ),
    url(r'^option/paginate/', views.options_paginate, name='options_paginate'),
    
    ]

if settings.DEBUG:
    # urlpatterns += [ url(r'^static/(?P<path>.*)$', serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)