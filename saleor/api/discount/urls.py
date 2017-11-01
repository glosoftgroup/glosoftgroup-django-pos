from django.conf.urls import url

from .views import (
    CustomerDiscountListAPIView,
    DiscountListAPIView  
    )


urlpatterns = [
    url(r'^customer/(?P<pk>[0-9]+)/$', CustomerDiscountListAPIView.as_view(), name='customer-discount-list-api'),
    url(r'^$', DiscountListAPIView.as_view(), name='api-discount-list'),
]

