from django.db.models import Q
from .serializers import (
    CustomerListSerializer,
    CreditWorthyCustomerSerializer,
    CustomerUpdateSerializer
)
from rest_framework import generics, status, serializers
from ...customer.models import Customer
import re
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
        is_name_queried = self.request.GET.get('isName')

        if query:

            if is_name_queried and "true" in is_name_queried:

                """ check if name matches """
                queryset_list = queryset_list.filter(
                    Q(name__icontains=query)
                ).distinct()

            elif is_name_queried and "false" in is_name_queried:

                """ validate number """

                self.validate_mobile(query)

                queryset_list = queryset_list.filter(
                    Q(mobile__icontains=query)
                ).distinct()

            else:
                queryset_list = queryset_list.filter(
                    Q(name__icontains=query) |
                    Q(mobile__icontains=query)
                ).distinct()
        return queryset_list

    def validate_mobile(self, value):

        """ Raise a ValidationError if not digits and if they exceed 14 digits.
        """
        rule = re.compile('^[0-9]{0,14}$')

        if not rule.match(value):
            raise serializers.ValidationError(
                {"Bad Request": "Invalid Number Format"},
                code=status.HTTP_400_BAD_REQUEST)


class CustomerDetailAPIView(generics.RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerListSerializer


class CustomerUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerUpdateSerializer
