from django.conf.urls import url

from .views import (
    CarListAPIView
    )


urlpatterns = [
    url(r'^$', CarListAPIView.as_view(), name='api-car-list'),
]

