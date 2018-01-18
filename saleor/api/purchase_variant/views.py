from rest_framework import generics
from ...purchase.models import PurchaseVariant as Table
from .serializers import (
    TableCreateSerializer,
)


class PurchaseCreateAPIView(generics.CreateAPIView):
    '''
        create a fully paid product variant purchases
    '''
    queryset = Table.objects.all()
    serializer_class = TableCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

