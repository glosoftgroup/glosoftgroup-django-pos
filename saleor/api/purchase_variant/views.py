from rest_framework import generics
from ...purchase.models import PurchaseVariant as Table
from .serializers import (
    TableCreateSerializer,
    TableListSerializer
)


class PurchaseCreateAPIView(generics.CreateAPIView):
    '''
        create a fully paid product variant purchases
    '''
    queryset = Table.objects.all()
    serializer_class = TableCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PurchaseListAPIView(generics.ListAPIView):
    serializer_class = TableListSerializer
    queryset = Table.objects.all().order_by('-id')

