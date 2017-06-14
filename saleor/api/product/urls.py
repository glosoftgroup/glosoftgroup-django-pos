from django.conf.urls import url

from .views import (
    CreateStockAPIView,
    ProductListAPIView,
    ProductStockListAPIView,
    UserListAPIView,
    UserDetailAPIView,
    UserCreateAPIView,
    UserDeleteAPIView,   
    PermissionListView,
    PermissionDetailAPIView,
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
    url(r'^customer/list/$', UserListAPIView.as_view(), name='user-list'),
    url(r'^customer/register/$', UserCreateAPIView.as_view(), name='register'),
    url(r'^users-details/(?P<pk>[0-9]+)/$', UserDetailAPIView.as_view(), name='detail'),    
    url(r'^user-delete/(?P<pk>[0-9]+)/$', UserDeleteAPIView.as_view(), name='user-delete'),
    url(r'^list-orders/$', SalesListAPIView.as_view(), name='list-orders'),
    url(r'^create-order/$', SalesCreateAPIView.as_view(), name='create-order'),
    url(r'^sales-details/(?P<pk>[0-9]+)/$', SalesDetailAPIView.as_view(), name='sales-details'),
    url(r'^sales-delete/(?P<pk>[0-9]+)/$', SalesDeleteAPIView.as_view(), name='sales-delete'),

    #permissions url patterns
    url(r'^permission-details/(?P<pk>[0-9]+)/$', PermissionDetailAPIView.as_view(), name='permission-detail'),
    url(r'^permissions', PermissionListView.as_view(), name='permissions')

]

