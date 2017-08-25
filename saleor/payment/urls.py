from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='payment'),
    url(r'^payments/$',views.payments_list, name='list-payments')
]
