from django.db.models import Q

from .pagination import PostLimitOffsetPagination, PostPageNumberPagination
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter
)
from rest_framework.decorators import api_view
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    )

from rest_framework.generics import (ListAPIView,                                     
                                     RetrieveAPIView,                                    
                                     RetrieveUpdateAPIView)
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.models import Permission

from ...payment.models import MpesaPayment
from .serializers import (
     MpesaPaymentListSerializer  
     )
from rest_framework import generics


        
class MpesaPaymentDetailAPIView(generics.RetrieveAPIView):
    queryset = MpesaPayment.objects.all()
    serializer_class = MpesaPaymentListSerializer


class MpesaPaymentListAPIView(generics.ListAPIView):
    queryset = MpesaPayment.objects.all()
    serializer_class = MpesaPaymentListSerializer

class MpesaPaymentListAPIView(generics.ListAPIView):       
    pagination_class = PostLimitOffsetPagination
    serializer_class = MpesaPaymentListSerializer

    def get_queryset(self, *args, **kwargs):        
        queryset_list = MpesaPayment.objects.all().select_related()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(ref_number__icontains=query)|
                Q(phone__sku__icontains=query)                
                ).distinct()
        return queryset_list
