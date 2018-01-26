from django.conf.urls import url

from .views import (
    PurchaseCreateAPIView,
    PurchaseListAPIView,
    PurchaseSupplierListAPIView,
    PurchaseHistoryListAPIView
    )


urlpatterns = [
    url(r'^$', PurchaseListAPIView.as_view(), name='list-variant-purchase'),
    url(r'^supplier/$', PurchaseSupplierListAPIView.as_view(), name='list-supplier-purchase'),
    url(r'^list/(?P<pk>[0-9]+)/$', PurchaseListAPIView.as_view(), name='api-list-purchase'),
    url(r'^history/(?P<pk>[0-9]+)/$', PurchaseHistoryListAPIView.as_view(), name='api-list-history'),
    url(r'^create/$', PurchaseCreateAPIView.as_view(), name='create-variant-purchase'),

]

