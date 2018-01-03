from django.conf.urls import url

from .views import (
    TableListAPIView,
    )


urlpatterns = [
    url(r'^$', TableListAPIView.as_view(), name='api-attribute-list'),
]

