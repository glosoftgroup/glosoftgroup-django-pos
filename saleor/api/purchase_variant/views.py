from rest_framework import generics
from django.db.models import Q
from rest_framework import pagination

from .pagination import PostLimitOffsetPagination
from ...purchase.models import PurchaseVariant as Table
from ...purchase.models import PurchaseVariantHistoryEntry as History
from .serializers import (
    TableCreateSerializer,
    TableListSerializer,
    HistorySerializer
)


class PurchaseCreateAPIView(generics.CreateAPIView):
    '''
        create a fully paid product variant purchases
    '''
    queryset = Table.objects.all()
    serializer_class = TableCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PurchaseListAPIViewbak(generics.ListAPIView):
    serializer_class = TableListSerializer
    queryset = Table.objects.all().order_by('-id')


# reports view
class PurchaseSupplierListAPIView(generics.ListAPIView):
    serializer_class = TableListSerializer
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
                Q(supplier__name__icontains=query)
            ).distinct('supplier')
        return queryset_list.order_by('supplier')


class PurchaseListAPIView(generics.ListAPIView):
    serializer_class = TableListSerializer
    pagination_class = PostLimitOffsetPagination

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs['pk']:
                pk = Table.objects.get(pk=self.kwargs['pk']).supplier.pk
                queryset_list = Table.objects.filter(supplier__pk=pk).select_related()
            if self.request.GET.get('date'):
                queryset_list = queryset_list.filter(supplier__pk=pk).filter(created__icontains=self.request.GET.get('date'))

        except Exception as e:
            queryset_list = Table.objects.all().select_related()
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('status'):
            if str(self.request.GET.get('status')) == 'all':
                pass
            else:
                queryset_list = queryset_list.filter(status=str(self.request.GET.get('status')))

        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(invoice_number__icontains=query)
                ).distinct()
        return queryset_list.order_by('-id')


class PurchaseHistoryListAPIView(generics.ListAPIView):
    """
        list purchase payment history
        :param pk purchase id
    """
    serializer_class = HistorySerializer
    pagination_class = PostLimitOffsetPagination

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs['pk']:
                queryset_list = History.objects.filter(purchase__pk=self.kwargs['pk'])

        except Exception as e:
            queryset_list = History.objects.all().select_related()
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        return queryset_list.order_by('-id')