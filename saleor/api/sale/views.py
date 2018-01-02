from django.db.models import Q
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model

from ...sale.models import Sales as Table
from ...sale.models import SoldItem as Item

from .serializers import (
    ItemSerializer,
    ListSerializer,
     )

User = get_user_model()

factory = APIRequestFactory()
request = factory.get('/')
serializer_context = {
    'request': Request(request),
}


class SaleListAPIView(generics.ListAPIView):
    """
        List Sales and sold items on each sale
        @:method GET /api/sale/
        payload Json: /payload/sales-list.json
    """
    serializer_class = ListSerializer

    def get_queryset(self, *args, **kwargs):        
        queryset_list = Table.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(invoice_number__icontains=query)               
                ).distinct()
        return queryset_list


class SaleItemsListAPIView(generics.ListAPIView):
    """
        List sold item list
        @:method GET
        payload Json: /payload/sold items.json
    """
    serializer_class = ItemSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = Item.objects.all().order_by('-id')
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(product_name__icontains=query)
                ).distinct()
        return queryset_list

