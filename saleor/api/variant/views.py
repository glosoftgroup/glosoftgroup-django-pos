from ...product.models import ProductVariant
from .serializers import (
    VariantListSerializer,
     )
from .pagination import PostLimitOffsetPagination
from django.db.models import Q
from rest_framework import pagination
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth import get_user_model
User = get_user_model()


class VariantListAPIView(generics.ListAPIView):
    """
        List Product variants
    """
    serializer_class = VariantListSerializer
    pagination_class = PostLimitOffsetPagination
    queryset = ProductVariant.objects.get_in_stock()

    def get_queryset(self, *args, **kwargs):
        queryset_list = ProductVariant.objects.all().select_related()

        # pagination size
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('supplier'):
            queryset_list = queryset_list.filter(variant_supplier__pk=int(self.request.GET.get('supplier')))
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(product__name__icontains=query) |
                Q(sku__icontains=query) |
                Q(variant_supplier__name__icontains=query)
                ).distinct()
        return queryset_list.order_by('-id')


class VariantCategoryListAPIView(generics.ListAPIView):
    serializer_class = VariantListSerializer
    queryset = ProductVariant.objects.get_in_stock()

    def list(self, request, pk=None):
        queryset = self.get_queryset().filter(product__categories__pk=pk).distinct('sku')
        serializer = VariantListSerializer(queryset, many=True)
        return Response(serializer.data)


class VariantProductListAPIView(generics.ListAPIView):
    """
        list variant for a certain product
        exclude variant with existing stock
        :param pk product id
    """
    serializer_class = VariantListSerializer
    queryset = ProductVariant.objects.all()

    def get_queryset(self, *args, **kwargs):
        queryset_list = ProductVariant.objects.all().select_related()

        # pagination size
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('supplier'):
            queryset_list = queryset_list.filter(variant_supplier__pk=int(self.request.GET.get('supplier')))

        # queryset_list = queryset_list.exclude(stock__quantity__gte=0).filter(product__pk=int(self.kwargs['pk']))
        queryset_list = queryset_list.filter(product__pk=int(self.kwargs['pk']))
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(sku__icontains=query)
            ).distinct()
        return queryset_list.order_by('-id')