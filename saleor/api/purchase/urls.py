from django.conf.urls import url

from .views import (
    PurchaseListAPIView,
    PurchaseSupplierListAPIView

    )


urlpatterns = [
    url(r'^$', PurchaseSupplierListAPIView.as_view(), name='list-supplier-purchase'),
    url(r'^list/(?P<pk>[0-9]+)/$', PurchaseListAPIView.as_view(), name='api-list-purchase'),

    
]

