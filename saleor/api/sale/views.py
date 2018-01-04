from django.db.models import Q, Sum, Count
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.test import APIRequestFactory
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from ...sale.models import Sales as Table
from ...sale.models import SoldItem as Item
from ...product.models import AttributeChoiceValue

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
            summary = Item.objects.values('product_name', 'attributes').filter(created__icontains=date).filter(attributes__has_key=key)
        else:
            summary = Item.objects.values('product_name', 'attributes').filter(attributes__has_key=key)
        report = []
        checker = []
        for i in summary:
            name = AttributeChoiceValue.objects.get(pk=int(i['attributes'][key])).name
            temp2 = {}
            temp = eval("Item.objects.values('product_name', 'attributes').filter(attributes__"+key+"="+i['attributes'][key]+").annotate(c=Count('attributes', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity'))")
            quantity = 0
            sum = 0
            for count in temp:
                quantity += count['quantity__sum']
                sum += count['total_cost__sum']
            temp2['quantity'] = quantity
            temp2['sum'] = sum
            temp2['attribute_value'] = name
            if i['attributes'][key] not in checker:
                report.append(temp2)
                checker.append(i['attributes'][key])

        return Response(report)


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

