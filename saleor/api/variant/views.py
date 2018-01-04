from ...product.models import ProductVariant
from .serializers import (
    VariantListSerializer,
     )
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth import get_user_model
User = get_user_model()


class VariantCategoryListAPIView(generics.ListAPIView):
    serializer_class = VariantListSerializer
    queryset = ProductVariant.objects.get_in_stock()

    def list(self, request, pk=None):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset().filter(product__categories__pk=pk)
        serializer = VariantListSerializer(queryset, many=True)
        return Response(serializer.data)