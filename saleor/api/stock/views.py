import datetime
from rest_framework import generics
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import pagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from .pagination import PostLimitOffsetPagination

from saleor.product.models import Stock as Table
from saleor.countertransfer.models import CounterTransferItems as CounterItems
from saleor.core.utils.closing_time import is_business_time
from .serializers import (
    CreateListSerializer,
    TableListSerializer,
    UpdateSerializer,
    SearchTransferredStockListSerializer
)
from structlog import get_logger

logger = get_logger(__name__)

User = get_user_model()
request = APIRequestFactory().get('/')
serializer_context = {
    'request': Request(request),
}


class CreateAPIView(generics.CreateAPIView):
    queryset = Table.objects.all()
    serializer_class = CreateListSerializer


class DestroyView(generics.DestroyAPIView):
    queryset = Table.objects.all()


class ListAPIView(generics.ListAPIView):
    """
        list details
        GET /api/setting/
    """
    serializer_class = TableListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PostLimitOffsetPagination

    def get_queryset(self, *args, **kwargs):
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10

        queryset_list = Table.objects.filter(quantity__gte=1).select_related()

        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        if category:
            queryset_list = queryset_list.filter(variant__product__categories__id=category)
        if query:
            queryset_list = queryset_list.filter(
                Q(variant__sku__icontains=query) |
                Q(variant__product__name__icontains=query) |
                Q(variant__product__description__icontains=query)
            ).distinct()
        return queryset_list


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


class SearchTransferredStockListAPIView(APIView):
    def get(self, request):

        query = self.request.GET.get('q', '')
        today = datetime.date.today()
        show_yesterday = is_business_time()
        today = datetime.date.today()
        if show_yesterday:
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
        else:
            yesterday = today
        all_counter_menu_stock = []
        """ get the counter stocks """
        try:
            counter_stock = CounterItems.objects.filter(
                Q(transfer__date=today) |
                Q(transfer__date=yesterday)
            ).filter(qty__gte=1).distinct('stock').select_related()

            if query:
                counter_stock = counter_stock.filter(
                    Q(stock__variant__sku__icontains=query) |
                    Q(stock__variant__product__name__icontains=query) |
                    Q(counter__name__icontains=query)).order_by('stock')

            if counter_stock.exists():
                for i in counter_stock:
                    """ set the json data fields 
                        using getCounterItemsJsonData(obj)
                    """
                    all_counter_menu_stock.append(getCounterItemsJsonData(i))


        except Exception as e:
            """ log error """
            logger.info('Error in getting counter stock: ' + str(e))
            pass

        serializer = SearchTransferredStockListSerializer(all_counter_menu_stock, many=True)
        return Response(serializer.data)


""" set the counter items json """


def getCounterItemsJsonData(obj):
    """ id """
    id = obj.id

    """ sku """
    try:
        sku = obj.stock.variant.sku
    except:
        sku = ''

    """ product_name """
    try:
        product_name = obj.productName
    except:
        product_name = ''

    """ product_category """
    try:
        product_category = obj.product_category
    except:
        product_category = ''

    """ counter """
    try:
        counter = {"id": obj.counter.id, "name": obj.counter.name}
    except:
        counter = None

    """ unit_cost """
    try:
        unit_cost = obj.stock.price_override.gross
    except:
        unit_cost = obj.unit_price

    """ quantity """
    try:
        quantity = CounterItems.objects.instance_quantities(obj.stock, filter_type='stock', counter=obj.counter)
    except:
        quantity = 0

    """ tax """
    try:
        tax = obj.tax
    except:
        tax = 0

    """ discount """
    try:
        discount = obj.discount
    except:
        discount = 0

    json_data = {
        "id": id,
        "sku": sku,
        "quantity": quantity,
        "product_name": product_name,
        "product_category": product_category,
        "unit_cost": unit_cost,
        "tax": tax,
        "discount": discount,
        "counter": counter,
        "kitchen": None
    }

    return json_data
