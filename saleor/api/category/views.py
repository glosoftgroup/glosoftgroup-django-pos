from rest_framework import generics
from rest_framework.response import Response
from rest_framework.request import Request
from django.contrib.auth import get_user_model
from .pagination import PostLimitOffsetPagination

from .serializers import (
    CategoryListSerializer,
     )
from ...product.models import Category

User = get_user_model()


class CategoryListAPIView(generics.ListAPIView):
    """ Serializer to list categories """
    serializer_class = CategoryListSerializer
    pagination_class = PostLimitOffsetPagination
    queryset = Category.objects.all()


class SalePointCategoryListAPIView(generics.ListAPIView):
    serializer_class = CategoryListSerializer
    queryset = Category.objects.all()

    def list(self, request, pk=None):
        serializer_context = {
            'request': Request(request),
        }
        queryset = self.get_queryset().filter(sale_point__pk=pk)
        serializer = CategoryListSerializer(queryset, context=serializer_context, many=True)
        return Response(serializer.data)

