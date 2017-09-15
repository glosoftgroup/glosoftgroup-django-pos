from django.db.models import Q

from .pagination import PostLimitOffsetPagination

from django.contrib.auth import get_user_model
User = get_user_model()

from ...payment.models import MpesaPayment
from ...sale.models import PaymentOption
from .serializers import (
     MpesaPaymentListSerializer,
     MpesaPaymentUpdateSerializer,
     PaymentOptionListSerializer
     )
from rest_framework import generics

class MpesaPaymentUpdateAPIView(generics.RetrieveUpdateAPIView):
        queryset = MpesaPayment.objects.all()
        serializer_class = MpesaPaymentUpdateSerializer
        
class MpesaPaymentDetailAPIView(generics.RetrieveAPIView):
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
                (Q(ref_number__icontains=query)|
                Q(first_name__icontains=query)|
                Q(last_name__icontains=query)|
                Q(middle_name__icontains=query)|
                Q(phone__icontains=query)) &
                Q(status=1)               
                ).order_by('-id').distinct()
        return queryset_list


class PaymentOptionsListAPIView(generics.ListAPIView):
    serializer_class = PaymentOptionListSerializer
    queryset = PaymentOption.objects.all()