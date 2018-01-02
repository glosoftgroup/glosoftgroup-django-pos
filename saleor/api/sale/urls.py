from django.conf.urls import url

from .views import (
    SaleListAPIView,
    SaleItemsListAPIView
    )


urlpatterns = [
    url(r'^$', SaleListAPIView.as_view(),
        name='list-sales'),
    url(r'^items/$', SaleItemsListAPIView.as_view(),
        name='list-sold-items'),
]

