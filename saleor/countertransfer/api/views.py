import datetime
from rest_framework import generics
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import pagination
from .pagination import PostLimitOffsetPagination
from saleor.countertransfer.models import CounterTransfer as Table
from saleor.product.models import Stock
from saleor.countertransfer.models import CounterTransferItems as Item
from .serializers import (
    CloseTransferItemSerializer,
    CreateListSerializer,
    TableListSerializer,
    UpdateSerializer,
    UpdateTransferItemSerializer,
    ItemsSerializer,
    ItemsStockSerializer
     )
from saleor.core.utils.closing_time import is_business_time
from ...decorators import user_trail
User = get_user_model()


class CreateAPIView(generics.CreateAPIView):
    queryset = Table.objects.all()
    serializer_class = CreateListSerializer

    def perform_create(self, serializer):
        serializer.user = self.request.user
        serializer.save(user=self.request.user)
        user_trail(self.request.user.name,
                   'made a counter transfer:#' + str(serializer.data['date']), 'add')


class DestroyView(generics.DestroyAPIView):
    queryset = Table.objects.all()

    def perform_destroy(self, instance):
        items = instance.counter_transfer_items.all()
        for item in items:
            Stock.objects.increase_stock(item.stock, item.qty)
        # raise serializers.ValidationError('You cannot delete ')
        if instance.any_closed():
            instance.trashed = True
            instance.save()
        else:
            instance.delete()


class DestroyItemView(generics.DestroyAPIView):
    queryset = Item.objects.all()

    def perform_destroy(self, instance):
        Stock.objects.increase_stock(instance.stock, instance.qty)
        # raise serializers.ValidationError('You cannot delete ')
        if instance.closed:
            instance.trashed = True
            instance.save()
        else:
            instance.delete()


class ListAPIView(generics.ListAPIView):
    """
        list details
        GET /api/setting/
    """
    serializer_class = TableListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PostLimitOffsetPagination

    def get_serializer_context(self):
        if self.request.GET.get('date'):
            return {"date": self.request.GET.get('date'), 'request': self.request}
        return {"date": None, 'request': self.request}

    def get_queryset(self, *args, **kwargs):
        queryset_list = Table.objects.filter(trashed=False)
        try:
            if self.kwargs['pk']:
                queryset_list = queryset_list.filter(customer__pk=self.kwargs['pk']).order_by('car').distinct('car').select_related()
        except Exception as e:
            pass

        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(date__icontains=self.request.GET.get('date'))

        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(counter__name__icontains=query))
        return queryset_list.order_by('-id')


class ListItemsAPIView(generics.ListAPIView):
    """
        list details
        GET /api/setting/
    """
    serializer_class = ItemsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PostLimitOffsetPagination

    def list(self, request, *args, **kwargs):
        response = super(ListItemsAPIView, self).list(request, args, kwargs)
        try:
            instance = Item.objects.filter(transfer__pk=self.kwargs['pk']).first()
            response.data['counter'] = instance.transfer.counter.name
            response.data['date'] = instance.transfer.date
            response.data['instance_id'] = instance.transfer.id

        except:
            pass
        return response

    def get_serializer_context(self):
        if self.request.GET.get('date'):
            return {"date": self.request.GET.get('date'), 'request': self.request}
        return {"date": None, 'request': self.request}

    def get_queryset(self, *args, **kwargs):
        queryset_list = Item.objects.filter(trashed=False)
        try:
            if self.kwargs['pk']:
                queryset_list = queryset_list.filter(transfer__pk=self.kwargs['pk']).select_related()
        except Exception as e:
            pass

        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(date__icontains=self.request.GET.get('date'))

        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(stock__variant__sku__icontains=query) |
                Q(stock__variant__product__name__icontains=query))
        return queryset_list.order_by('-id')


class ListStockAPIView(generics.ListAPIView):
    """
        list details
        GET /api/setting/
    """
    serializer_class = ItemsStockSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PostLimitOffsetPagination

    def list(self, request, *args, **kwargs):
        response = super(ListStockAPIView, self).list(request, args, kwargs)
        try:
            instance = Item.objects.filter(transfer__pk=self.kwargs['pk']).first()
            response.data['counter'] = instance.transfer.counter.name
            response.data['date'] = instance.transfer.date
        except:
            pass
        return response

    def get_serializer_context(self):
        if self.request.GET.get('date'):
            return {"date": self.request.GET.get('date'), 'request': self.request}
        return {"date": None, 'request': self.request}

    def get_queryset(self, *args, **kwargs):
        # determine whether to show yesterdays transfer
        # This will enable selling today's stock after mid day
        show_yesterday = is_business_time()
        today = datetime.date.today()
        if show_yesterday:
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
        else:
            yesterday = today

        try:
            if self.kwargs['pk']:
                queryset_list = Item.objects.filter(
                    Q(transfer__date=today) |
                    Q(transfer__date=yesterday)
                ).filter(transfer__counter__pk=self.kwargs['pk'])\
                    .distinct('stock').select_related()
            else:
                queryset_list = Item.objects.filter(
                    Q(transfer__date=today) |
                    Q(transfer__date=yesterday)
                ).distinct('stock').select_related()
        except Exception as e:
            queryset_list = Item.objects.all().filter(
                Q(transfer__date=today) |
                Q(transfer__date=yesterday)
            ).distinct('stock')

        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(transfer__date__icontains=self.request.GET.get('date'))

        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(stock__variant__sku__icontains=query) |
                Q(stock__variant__product__name__icontains=query))
        return queryset_list.order_by('stock')


class ListCategoryAPIView(generics.ListAPIView):
    """
        list transferred stock in {pk} category
        :param pk category pk
        GET /counter/transfer/api/list/category/1/

        Json payload => /payload/category-items.json
    """
    serializer_class = ItemsStockSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PostLimitOffsetPagination

    def get_serializer_context(self):
        if self.request.GET.get('date'):
            return {"date": self.request.GET.get('date'), 'request': self.request}
        return {"date": None, 'request': self.request}

    def get_queryset(self, *args, **kwargs):
        show_yesterday = is_business_time()
        today = datetime.date.today()
        if show_yesterday:
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
        else:
            yesterday = today

        queryset_list = Item.objects.filter(qty__gte=1)
        try:
            if self.kwargs['pk']:
                queryset_list = queryset_list.filter(
                    Q(transfer__date=today) |
                    Q(transfer__date=yesterday)
                ).filter(stock__variant__product__categories__pk=self.kwargs['pk'])

            else:
                queryset_list = Item.objects.filter(
                    Q(transfer__date=today) |
                    Q(transfer__date=yesterday)
                )
        except Exception as e:
            queryset_list = Item.objects.all().filter(
                Q(transfer__date=today) |
                Q(transfer__date=yesterday)
            )

        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 8
        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(date__icontains=self.request.GET.get('date'))

        if self.request.GET.get('counter'):
            queryset_list = queryset_list.filter(counter__pk=self.request.GET.get('counter'))

        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(stock__variant__sku__icontains=query) |
                Q(stock__variant__product__name__icontains=query))
        return queryset_list.distinct('stock').select_related().order_by('stock')


class UpdateAPIView(generics.RetrieveUpdateAPIView):
    """
        update instance details
        @:param pk house id
        @:method PUT

        PUT /api/house/update/
        payload Json: /payload/update.json
    """
    queryset = Table.objects.all()
    serializer_class = UpdateSerializer


class UpdateItemAPIView(generics.RetrieveUpdateAPIView):
    """
        update instance details
        @:param pk id
        @:method PUT

        PUT /api/house/update/
        payload Json: /payload/update.json
    """
    queryset = Item.objects.all()
    serializer_class = UpdateTransferItemSerializer


class CloseItemAPIView(generics.RetrieveUpdateAPIView):
    """
        update instance details
        @:param pk id
        @:method PUT

        PUT /api/house/update/
        payload Json: /payload/update.json
    """
    queryset = Item.objects.all()
    serializer_class = CloseTransferItemSerializer
