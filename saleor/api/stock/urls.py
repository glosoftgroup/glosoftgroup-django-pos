from django.conf.urls import url

from .views import *


urlpatterns = [
    url(r'^$', ListAPIView.as_view(), name='api-stock-list'),
    url(r'^list/$', ListAPIView.as_view(), name='api-stock-list'),
    url(r'^search/transfer/$', SearchTransferredStockListAPIView.as_view(), name='api-stock-transfer-list'),
]

