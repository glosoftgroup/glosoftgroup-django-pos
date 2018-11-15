import datetime
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
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
    ItemsStockSerializer,
    SnippetSerializer
     )
from saleor.core.utils.closing_time import is_business_time
User = get_user_model()


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
        try:
            if self.kwargs['pk']:
                queryset_list = Table.objects.filter(customer__pk=self.kwargs['pk']).order_by('car').distinct('car').select_related()
            else:
                queryset_list = Table.objects.all.select_related()
        except Exception as e:
            queryset_list = Table.objects.all()

        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        mode = self.request.GET.get('mode')
        date = self.request.GET.get('date')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date:
            year = date.split("-")[0]
            if len(date.split('-')) >= 2:
                month = date.split("-")[1]
            else:
                month = "01"
            if mode == "month":
                queryset_list = queryset_list.filter(date__year=year,
                                                     date__month=month)
            elif mode == "year":
                queryset_list = queryset_list.filter(date__year=year)
            else:
                queryset_list = queryset_list.filter(date__icontains=date)
        # filter date range
        elif date_from and date_to:
            if mode:
                year_from = date_from.split("-")[0]
                if len(date_from.split('-')) >= 2:
                    month_from = date_from.split("-")[1]
                else:
                    month_from = "01"

                year_to = date_to.split("-")[0]
                if len(date_to.split('-')) >= 2:
                    month_to = date_to.split("-")[1]
                else:
                    month_to = "01"

                if mode == "month":
                    queryset_list = queryset_list.filter(date__year__gte=year_from,
                                                         date__month__gte=month_from,
                                                         date__year__lte=year_to,
                                                         date__month__lte=month_to)
                elif mode == "year":
                    queryset_list = queryset_list.filter(date__year__gte=year_from,
                                                         date__year__lte=year_to)
                else:
                    queryset_list = queryset_list.filter(date__range=[date_from, date_to])
            else:
                queryset_list = queryset_list.filter(date__range=[date_from, date_to])

        if self.request.GET.get('counter'):
            queryset_list = queryset_list.filter(counter__pk=self.request.GET.get('counter'))
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
        try:
            if self.kwargs['pk']:
                queryset_list = Item.objects.filter(transfer__pk=self.kwargs['pk']).select_related()
            else:
                queryset_list = Item.objects.all.select_related()
        except Exception as e:
            queryset_list = Item.objects.all()

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


class SnippetList(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        query = Table.objects.all_items_filter(start_date, end_date)
        serializer = SnippetSerializer(query, many=True)
        return Response(query)


class HighchartPieList(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        mode = self.request.GET.get('mode')
        date = self.request.GET.get('date')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        counter = self.request.GET.get('counter')
        query = Table.objects.highcharts_pie_filter(date_from, date_to, date, mode, counter)
        return Response(query)


class RechartsList(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        mode = self.request.GET.get('mode')
        date = self.request.GET.get('date')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        counter = self.request.GET.get('counter')
        query = Table.objects.recharts_items_filter(date_from, date_to, date, mode, counter)
        return Response(query)


class HighchartCounterList(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        mode = self.request.GET.get('mode')
        date = self.request.GET.get('date')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        # query = Table.objects.highcharts_line_filter(date_from, date_to, date, mode)
        query = Item.objects.top_products()
        return Response(query)


class TopProducts(APIView):
    def get(self, request, format=None):
        mode = self.request.GET.get('mode')
        date = self.request.GET.get('date')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        counter = self.request.GET.get('counter')
        query_type = self.request.GET.get('query_type')
        query = Item.objects.top_products(date_from, date_to, date, mode, counter, query_type)
        return Response(query)


class RechartsListTotal(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        query = Table.objects.recharts_items_price(start_date, end_date)
        return Response(query)
