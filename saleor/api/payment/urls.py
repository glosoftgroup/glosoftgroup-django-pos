from django.conf.urls import url

from .views import (
    MpesaPaymentDetailAPIView,
    MpesaPaymentListAPIView,
    MpesaPaymentUpdateAPIView
    )


urlpatterns = [
    url(r'^$', MpesaPaymentListAPIView.as_view(), name='mpesa-list'),
    url(r'^mpesa-update/(?P<pk>[0-9]+)/$',MpesaPaymentUpdateAPIView.as_view(), name='mpesa-update'),
    url(r'^mpesa-payment-details/(?P<pk>[0-9]+)/$', MpesaPaymentDetailAPIView.as_view(), name='mpesa-detail'),    
    
]

