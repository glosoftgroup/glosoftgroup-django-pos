from django.conf.urls import url

from .views import (
    CreateStockAPIView,
    CustomerListAPIView,
    CustomerDetailAPIView,
    ProductListAPIView,
    ProductStockListAPIView,
    SearchSkuListAPIView,
    SalesListAPIView,
    SalesCreateAPIView,
    SalesDetailAPIView,
    SalesDeleteAPIView,
    )


urlpatterns = [
    url(r'^$', ProductListAPIView.as_view(), name='product-list'),
    url(r'^stock$', ProductStockListAPIView.as_view(), name='productstock-list'),
    url(r'^stock/(?P<stock_pk>[0-9]+)$', CreateStockAPIView.as_view(), name='create-stock'),
    url(r'^search-sku/$', SearchSkuListAPIView.as_view(), name='search-sku'),
    url(r'^customer/list/$', CustomerListAPIView.as_view(), name='customer-list'),
    url(r'^customer/list/$', CustomerListAPIView.as_view(), name='customer-list'),
    url(r'^customer-details/(?P<pk>[0-9]+)/$', CustomerDetailAPIView.as_view(), name='costomer-detail'),
    url(r'^list-orders/$', SalesListAPIView.as_view(), name='list-orders'),
    url(r'^create-order/$', SalesCreateAPIView.as_view(), name='create-order'),
    url(r'^sales-details/(?P<pk>[0-9]+)/$', SalesDetailAPIView.as_view(), name='sales-details'),
    url(r'^sales-delete/(?P<pk>[0-9]+)/$', SalesDeleteAPIView.as_view(), name='sales-delete'),

]

