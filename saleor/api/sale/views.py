from django.db.models import Q, Sum, Count
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.test import APIRequestFactory
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from ...sale.models import Sales as Table
from ...sale.models import SoldItem as Item

from .serializers import (
    ItemListSerializer,
    ItemSerializer,
    ListSerializer,
     )

User = get_user_model()

factory = APIRequestFactory()
request = factory.get('/')
serializer_context = {
    'request': Request(request),
}


class ItemListAPIView(APIView):
    def get(self, request, format=None, **kwargs):
        """
        Return a list of all sales.
        """
        key = ''
        if self.kwargs['pk']:
            key = self.kwargs['pk']
        if self.request.GET.get('date'):
            date = self.request.GET.get('date')
            summary = Item.objects.filter(created__icontains=date).values('product_name')\
                .filter(attributes__has_key=key).annotate(
                c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
                '-quantity__sum')
        else:
            summary = Item.objects.values('product_name').filter(attributes__has_key=key).annotate(
                c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
                '-quantity__sum')
        return Response(summary)


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
    serializer_class = ItemListSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = Item.objects.all().order_by('-id')
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(product_name__icontains=query)
                ).distinct()
        return queryset_list

