from django.conf.urls import url

from .views import (
    VariantCategoryListAPIView,
    VariantListAPIView
    )


urlpatterns = [
    url(r'^$', VariantListAPIView.as_view(), name='variant-list'),
    url(r'^category/(?P<pk>[0-9]+)$', VariantCategoryListAPIView.as_view(), name='api-variant-list'),
]

