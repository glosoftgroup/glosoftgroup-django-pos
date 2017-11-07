from .serializers import (
     UserListSerializer,
     )
from rest_framework import generics
from ...sale.models import Terminal
import logging
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.contrib.auth import get_user_model
User = get_user_model()


class UserListAPIView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = User.objects.all()


class AgentListAPIView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = User.objects.all()