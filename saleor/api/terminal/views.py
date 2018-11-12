from .serializers import (
     TerminalListSerializer,    
     )
from rest_framework import generics
from ...sale.models import Terminal

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.contrib.auth import get_user_model
User = get_user_model()


class TerminalListAPIView(generics.ListAPIView):
    serializer_class = TerminalListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Terminal.objects.all()
