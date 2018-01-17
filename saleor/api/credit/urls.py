from django.conf.urls import url

from .views import (    
    CreditCreateAPIView,
    CreditListAPIView,
    CreditorsListAPIView,
    CreditUpdateAPIView,
    CustomerDistinctListAPIView,
    CustomerCreditListAPIView
    )


urlpatterns = [
    url(r'^$', CreditListAPIView.as_view(), name='list-credit'),
    url(r'^search-credit/$', CreditorsListAPIView.as_view(), name='search-credit'),
    url(r'^update-credit/(?P<pk>[0-9]+)/$', CreditUpdateAPIView.as_view(), name='update-credit'),
    url(r'^create-credit/$', CreditCreateAPIView.as_view(), name='create-credit'),
    url(r'^customer/$', CustomerDistinctListAPIView.as_view(), name='customer-credit'),
    url(r'^list/(?P<pk>[0-9]+)/$', CustomerCreditListAPIView.as_view(), name='api-list-credit'),
    
]

