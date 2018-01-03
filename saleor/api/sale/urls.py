from django.conf.urls import url

from .views import (
    SaleListAPIView,
    ItemListAPIView,
    )


urlpatterns = [
    url(r'^$', SaleListAPIView.as_view(),
        name='list-sales'),
    url(r'^items/(?P<pk>[0-9]+)/$', ItemListAPIView.as_view(),
        name='list-sold-items'),
]

