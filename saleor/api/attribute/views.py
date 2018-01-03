from django.db.models import Q
from ...product.models import ProductAttribute as Table
from .pagination import PostLimitOffsetPagination
from .serializers import (
    TableListSerializer,
     )
from rest_framework import generics
from django.contrib.auth import get_user_model
User = get_user_model()


class TableListAPIView(generics.ListAPIView):
    """
        List product attributes
        :param q queryset search term
        :method GET /api/attribute/?q=Gas
    """
    serializer_class = TableListSerializer
    pagination_class = PostLimitOffsetPagination

    def get_queryset(self, *args, **kwargs):
        queryset_list = Table.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(name__icontains=query)
                ).distinct()

        return queryset_list