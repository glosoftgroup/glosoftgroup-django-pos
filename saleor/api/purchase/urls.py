from django.conf.urls import url

from .views import (
    PurchaseListAPIView,
    PurchaseSupplierListAPIView,
    PaymentListAPIView,
    PaymentOptionListAPIView

    )


urlpatterns = [
    url(r'^$', PurchaseSupplierListAPIView.as_view(), name='list-supplier-purchase'),
    url(r'^payment/option$', PaymentOptionListAPIView.as_view(), name='list-payment-options'),
    url(r'^list/(?P<pk>[0-9]+)/$', PurchaseListAPIView.as_view(), name='api-list-purchase'),
    url(r'^list/stock/(?P<pk>[0-9]+)/$', PaymentListAPIView.as_view(), name='api-list-stock-purchase'),

    
]

