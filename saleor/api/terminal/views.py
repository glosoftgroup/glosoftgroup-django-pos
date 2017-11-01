from .serializers import (
     TerminalListSerializer,    
     )
from rest_framework import generics
from ...sale.models import Terminal
import logging
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.contrib.auth import get_user_model
User = get_user_model()
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


class TerminalListAPIView(generics.ListAPIView):
    serializer_class = TerminalListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Terminal.objects.all()