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
from ...invoice.models import Invoice
from ...sale.models import (
                            Terminal, 
                            TerminalHistoryEntry,
                            )
from ...customer.models import Customer
from .serializers import (
    InvoiceListSerializer,
    CreateInvoiceSerializer,
     )
from rest_framework import generics

from ...decorators import user_trail
import logging
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


class InvoiceDetailAPIView(generics.RetrieveAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceListSerializer


class InvoiceCreateAPIView(generics.CreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = CreateInvoiceSerializer

    def perform_create(self, serializer):              
        serializer.save(user=self.request.user)      

        
class InvoiceListAPIView(generics.ListAPIView):
    serializer_class = InvoiceListSerializer

    def get_queryset(self, *args, **kwargs):        
        queryset_list = Invoice.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(invoice_number__icontains=query) |
                Q(customer__name__icontains=query) |
                Q(created__icontains=query) |
                Q(customer__mobile__icontains=query)
                ).distinct()
        return queryset_list


