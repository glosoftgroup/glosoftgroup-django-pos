from django.db.models import Q
from .serializers import (
     CustomerListSerializer,
     CreditWorthyCustomerSerializer,
     CustomerUpdateSerializer   
     )
from rest_framework import generics
from ...customer.models import Customer
import logging
from django.contrib.auth import get_user_model

User = get_user_model()
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')     


class CreditWorthyCustomerListAPIView(generics.ListAPIView):
    serializer_class = CreditWorthyCustomerSerializer
    def get_queryset(self, *args, **kwargs):        
        queryset_list = Customer.objects.filter(creditable=True)
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(name__icontains=query)               
                ).distinct()
        return queryset_list


class CustomerListAPIView(generics.ListAPIView):   
    serializer_class = CustomerListSerializer

    def get_queryset(self, *args, **kwargs):        
        queryset_list = Customer.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(name__icontains=query)|  
                Q(mobile__icontains=query)             
                ).distinct()
        return queryset_list


class CustomerDetailAPIView(generics.RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerListSerializer

class CustomerUpdateAPIView(generics.RetrieveUpdateAPIView):    
    queryset = Customer.objects.all()
    serializer_class = CustomerUpdateSerializer