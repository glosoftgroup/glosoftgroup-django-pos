from django.db.models import Q

from .pagination import PostLimitOffsetPagination, PostPageNumberPagination

from django.contrib.auth import get_user_model
User = get_user_model()

from ...sale.models import Terminal

from .serializers import (
     TerminalListSerializer,    
     )
from rest_framework import generics 
from rest_framework.response import Response
from django.contrib import auth
from ...decorators import user_trail
from ...sale.models import Terminal
import logging
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')     
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt, csrf_protect


class TerminalListAPIView(generics.ListAPIView):
    serializer_class = TerminalListSerializer
    queryset = Terminal.objects.all()