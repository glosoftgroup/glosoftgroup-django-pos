from django.db.models import Q
from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework import pagination

from notifications.models import Notification
from .pagination import PostLimitOffsetPagination
from .serializers import (
     MessagesListSerializer,
     )

import logging

User = get_user_model()
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


class MessagesListAPIView(generics.ListAPIView):
    serializer_class = MessagesListSerializer
    pagination_class = PostLimitOffsetPagination

    def get_serializer_context(self):
        if self.request.GET.get('date'):
            return {"date": self.request.GET.get('date'), 'request': self.request}
        return {"date": None, 'request': self.request}

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs['pk']:
                queryset_list = Notification.objects.filter(user__pk=self.kwargs['pk']).select_related()
            else:
                queryset_list = Notification.objects.all.select_related()
        except Exception as e:
            queryset_list = self.request.user.notifications # Notification.objects.all()
            query = self.request.GET.get('q')
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('status'):
            status = self.request.GET.get('status')
            if status == 'all':
                pass
            if status == 'trash':
                queryset_list = self.request.user.notifications.deleted()
            elif status == 'unread':
                queryset_list = self.request.user.notifications.unread()
            elif status == 'read':
                queryset_list = Notification.objects.filter(actor_object_id=self.request.user.id, unread=False)
            elif status == 'emailed':
                queryset_list = Notification.objects.filter(actor_object_id=self.request.user.id, emailed=True)

        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(timestamp__icontains=self.request.GET.get('date'))
        if query:
            queryset_list = queryset_list.filter(
                Q(verb__icontains=query) |
                Q(description__icontains=query) |
                Q(recipient__name__icontains=query)
                )
        return queryset_list.order_by('-id')