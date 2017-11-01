from django.conf.urls import url

from .views import (
    CategoryListAPIView,
    SalePointCategoryListAPIView,
    )


urlpatterns = [
    url(r'^$', CategoryListAPIView.as_view(), name='api-category-list'),
    url(r'^sale-point/(?P<pk>[0-9]+)$',
        SalePointCategoryListAPIView.as_view(),
        name='api-sale_point-categories'),
]

