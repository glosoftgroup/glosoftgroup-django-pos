from django.conf.urls import url

from .views import (
    CustomerListAPIView,
    CustomerDetailAPIView,
    CreditWorthyCustomerListAPIView,
    CustomerUpdateAPIView  
    )


urlpatterns = [
   url(r'^$', CustomerListAPIView.as_view(), name='customer-list'),   
   url(r'^details/(?P<pk>[0-9]+)/$', CustomerDetailAPIView.as_view(), name='customer-detail'),
   url(r'^credit-worthy/$', CreditWorthyCustomerListAPIView.as_view(),
     name='credit-worthy-customers'),
   url(r'^redeem-points/(?P<pk>[0-9]+)/$', CustomerUpdateAPIView.as_view(),
     name='update-customer-details-api'),    
]

