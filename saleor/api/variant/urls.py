from django.conf.urls import url

from .views import (
    VariantCategoryListAPIView
    )


urlpatterns = [
    url(r'^category/(?P<pk>[0-9]+)$', VariantCategoryListAPIView.as_view(), name='api-variant-list'),
]

