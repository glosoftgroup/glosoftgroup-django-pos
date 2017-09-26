from django.db.models import Q

from .pagination import PostLimitOffsetPagination, PostPageNumberPagination

from django.contrib.auth import get_user_model
User = get_user_model()

from ...sale.models import Terminal

from .serializers import (
	 DiscountListSerializer,
     CustomerDiscountListSerializer,    
     )
from rest_framework import generics 
from rest_framework.response import Response
from django.contrib import auth
from ...decorators import user_trail
from ...discount.models import Sale
from ...customer.models import Customer
import logging
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')     
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt, csrf_protect


class DiscountListAPIView(generics.ListAPIView):
    serializer_class = DiscountListSerializer
    queryset = Sale.objects.all()

class CustomerDiscountListAPIView(generics.RetrieveAPIView):
    serializer_class = CustomerDiscountListSerializer
    queryset = Customer.objects.all()