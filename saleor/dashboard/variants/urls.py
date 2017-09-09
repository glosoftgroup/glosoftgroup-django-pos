from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views

urlpatterns = [
    url(r'^$',permission_required('product.view_product', login_url='not_found')
    (views.variant_list), name='variant-list'),

    url(r'^(?P<pk>[0-9]+)/list/$',permission_required('product.view_product', login_url='not_found')
    (views.variant_list), name='product-variant-list'),
    url(r'^variant/paginate/$', views.variant_paginate, name='variant_paginate'),
    url(r'^(?P<pk>[0-9]+)/variant/paginate/$', views.variant_paginate, name='variant_paginate2'),
    url( r'^variant_search/$', views.variant_search, name = 'variant_search' ),
    url( r'^(?P<pk>[0-9]+)/variant_search/$', views.variant_search, name = 'variant_search2' ),
    
    ]