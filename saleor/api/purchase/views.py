from django.db.models import Q, Count, Avg

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import pagination

from .pagination import PostLimitOffsetPagination
from ...purchase.models import PurchaseProduct as Table
from saleor.payment.models import PaymentOption

from .serializers import (
    TableListSerializer,
    DistinctTableListSerializer,
    PaymentOptionListSerializer
     )
from rest_framework import generics

import logging
from django.contrib.auth import get_user_model

User = get_user_model()
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


class PurchaseListAPIView(generics.ListAPIView):
    serializer_class = TableListSerializer
    pagination_class = PostLimitOffsetPagination

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs['pk']:
                pk = Table.objects.get(pk=self.kwargs['pk']).supplier.pk
                queryset_list = Table.objects.filter(supplier__pk=pk).select_related()
            else:
                queryset_list = Table.objects.all().order_by('-id').select_related()
        except Exception as e:
            queryset_list = Table.objects.all().select_related()
        query = self.request.GET.get('q')
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('status'):
            if self.request.GET.get('status') == 'True':
                queryset_list = queryset_list.filter(active=True)
            if self.request.GET.get('status') == 'False':
                queryset_list = queryset_list.filter(active=False)
        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(created__icontains=self.request.GET.get('date'))
        if query:
            queryset_list = queryset_list.filter(
                Q(invoice_number__icontains=query) |
                Q(supplier__name__icontains=query)
                ).distinct()
        return queryset_list.order_by('-id')


class PurchaseSupplierListAPIView(generics.ListAPIView):
    serializer_class = DistinctTableListSerializer
    pagination_class = PostLimitOffsetPagination

    def get_serializer_context(self):
        if self.request.GET.get('date'):
            return {"date": self.request.GET.get('date'), 'request': self.request}
        return {"date": None, 'request': self.request}

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs['pk']:
                queryset_list = Table.objects.filter(customer__pk=self.kwargs['pk']).order_by('car').distinct('car').select_related()
            else:
                queryset_list = Table.objects.all.select_related()
        except Exception as e:
            queryset_list = Table.objects.distinct('supplier')
            query = self.request.GET.get('q')
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('status'):
            if self.request.GET.get('status') == 'True':
                queryset_list = queryset_list.filter(active=True)
            if self.request.GET.get('status') == 'False':
                queryset_list = queryset_list.filter(active=False)
        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(created__icontains=self.request.GET.get('date'))
        if query:
            queryset_list = queryset_list.filter(
                Q(invoice_number__icontains=query) |
                Q(car__number__icontains=query) |
                Q(car__name__icontains=query)
                ).distinct('supplier')
        return queryset_list.order_by('supplier')


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = TableListSerializer
    queryset = Table.objects.all()

    def list(self, request, pk=None):
        serializer_context = {
            'request': Request(request),
        }
        queryset = self.get_queryset().filter(stock__pk=pk)
        serializer = TableListSerializer(queryset, context=serializer_context, many=True)
        return Response(serializer.data)


class PaymentOptionListAPIView(generics.ListAPIView):
    serializer_class = PaymentOptionListSerializer
    pagination_class = PostLimitOffsetPagination

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs['pk']:
                pk = Table.objects.get(pk=self.kwargs['pk']).supplier.pk
                queryset_list = PaymentOption.objects.filter(supplier__pk=pk).select_related()
            else:
                queryset_list = PaymentOption.objects.all().order_by('-id').select_related()
        except Exception as e:
            queryset_list = PaymentOption.objects.all().select_related()
        query = self.request.GET.get('q')
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('status'):
            if self.request.GET.get('status') == 'True':
                queryset_list = queryset_list.filter(active=True)
            if self.request.GET.get('status') == 'False':
                queryset_list = queryset_list.filter(active=False)
        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(created__icontains=self.request.GET.get('date'))
        if query:
            queryset_list = queryset_list.filter(
                Q(name__icontains=query)
            ).distinct()
        return queryset_list.order_by('-id')

