import logging
from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .serializers import (
     TableListSerializer,
     )
from ...car.models import Car as Table


class CarListAPIView(generics.ListAPIView):
    serializer_class = TableListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    #queryset = Table.objects.all()
    def get_queryset(self, *args, **kwargs):
        queryset_list = Table.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(number__icontains=query) |
                Q(name__icontains=query)
                ).distinct()
        return queryset_list



