from django.conf.urls import url

from .views import (
    PurchaseCreateAPIView,
    PurchaseListAPIView
    )


urlpatterns = [
    url(r'^$', PurchaseListAPIView.as_view(), name='list-variant-purchase'),
    url(r'^/create/$', PurchaseCreateAPIView.as_view(), name='create-variant-purchase'),

]

