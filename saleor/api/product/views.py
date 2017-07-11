from django.db.models import Q
from .pagination import PostLimitOffsetPagination
from rest_framework.generics import (ListAPIView,
                                     CreateAPIView,
                                     RetrieveAPIView,
                                     DestroyAPIView,
                                    )
from django.contrib.auth import get_user_model
User = get_user_model()
from ...product.models import (
    Product,
    ProductVariant,
    Stock,
    )
from ...sale.models import (Sales, 
                            Terminal, 
                            TerminalHistoryEntry,
                            DrawerCash)
from ...customer.models import Customer
from .serializers import (
    CreateStockSerializer,
    CustomerListSerializer,
    ProductStockListSerializer,
    ProductListSerializer,
    SalesSerializer,  
     )
from rest_framework import generics

from ...decorators import user_trail
import logging
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


class CreateStockAPIView(CreateAPIView):
    serializer_class = CreateStockSerializer
    queryset = Stock.objects.all()


class CustomerListAPIView(ListAPIView):
    serializer_class = CustomerListSerializer
    queryset = Customer.objects.all()


class CustomerDetailAPIView(generics.RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerListSerializer


class SalesDeleteAPIView(DestroyAPIView):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer


class SalesDetailAPIView(generics.RetrieveAPIView):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer


class SalesCreateAPIView(generics.CreateAPIView):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer
    def perform_create(self, serializer):              
        serializer.save(user=self.request.user)
        user_trail(self.request.user.name,'made a sale:#'+str(serializer.data['invoice_number'])+' sale worth: '+str(serializer.data['total_net']),'add')
        info_logger.info('User: '+str(self.request.user)+' made a sale:'+str(serializer.data['invoice_number']))
        terminal = Terminal.objects.get(pk=int(serializer.data['terminal']))
        trail = 'User: '+str(self.request.user)+\
                ' made a sale:'+str(serializer.data['invoice_number'])+\
                ' Net#: '+str(serializer.data['total_net'])
        TerminalHistoryEntry.objects.create(
                            terminal=terminal,
                            comment=trail,
                            crud='deposit',
                            user=self.request.user
                        )
        drawer = DrawerCash.objects.create(manager=self.request.user,                                        
                                           user = self.request.user,
                                           terminal=terminal,
                                           amount=serializer.data['total_net'],
                                           trans_type='sale')
        


class SalesListAPIView(generics.ListAPIView):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer


class ProductListAPIView(generics.ListAPIView):
    pagination_class = PostLimitOffsetPagination
    serializer_class = ProductListSerializer

    def get_queryset(self, *args, **kwargs):        
        queryset_list = Product.objects.all().select_related()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(name__icontains=query)|
                Q(variants__sku__icontains=query)|
                Q(categories__name__icontains=query)
                ).distinct()
        return queryset_list


class SearchSkuListAPIView(generics.ListAPIView):
    pagination_class = PostLimitOffsetPagination
    serializer_class = ProductStockListSerializer

    def get_queryset(self, *args, **kwargs):        
        queryset_list = ProductVariant.objects.all().select_related()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                sku__startswith=query               
                ).distinct()
        return queryset_list


class ProductStockListAPIView(generics.ListAPIView):
    pagination_class = PostLimitOffsetPagination
    serializer_class = ProductStockListSerializer

    def get_queryset(self, *args, **kwargs):        
        queryset_list = ProductVariant.objects.all().select_related()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(sku__icontains=query) |
                Q(product__name__icontains=query)|
                Q(product__description__icontains=query)
                ).distinct()
        return queryset_list

