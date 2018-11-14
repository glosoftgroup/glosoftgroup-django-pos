from django.db.models import Q
from ...invoice.models import Invoice
from .serializers import (
    InvoiceListSerializer,
    CreateInvoiceSerializer,
     )
from rest_framework import generics


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


