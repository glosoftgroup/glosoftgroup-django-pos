from django.conf.urls import url

from .views import (
    MpesaPaymentDetailAPIView,
    MpesaPaymentListAPIView,
    )


urlpatterns = [
    url(r'^$', MpesaPaymentListAPIView.as_view(), name='mpesa-list'),
    url(r'^mpesa-payment-details/(?P<pk>[0-9]+)/$', MpesaPaymentDetailAPIView.as_view(), name='mpesa-detail'),    
    
]

