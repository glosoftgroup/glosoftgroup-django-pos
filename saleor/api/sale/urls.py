from django.conf.urls import url

from .views import (
    SoldItemListAPIView,
    ItemListAPIView,
    SaleMarginListAPIView
    )


urlpatterns = [
    url(r'^$', SoldItemListAPIView.as_view(),
        name='list-sales'),
    url(r'^margin/', SaleMarginListAPIView.as_view(),
        name='sale-margin'),
    url(r'^items/(?P<pk>[0-9]+)/$', ItemListAPIView.as_view(),
        name='list-sold-items'),
]

