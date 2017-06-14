from django.db.models import Q

from .pagination import PostLimitOffsetPagination, PostPageNumberPagination
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter
)
from rest_framework.decorators import api_view
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    )

from rest_framework.generics import (ListAPIView,
                                     CreateAPIView,
                                     RetrieveAPIView,
                                     DestroyAPIView,
                                     UpdateAPIView,
                                     RetrieveUpdateAPIView)
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.models import Permission
from ...product.models import (
    Product,
    ProductVariant,
    Stock,
    )
from ...sale.models import (Sales)
from ...order.models import Order
from .serializers import (
    CreateStockSerializer,
    ProductStockListSerializer,
    ProductListSerializer,
    UserListSerializer,    
    UserCreateSerializer,
    PermissionListSerializer,
    SalesSerializer,  
     )
from rest_framework import generics


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = User.objects.all()

class CreateStockAPIView(CreateAPIView):
    serializer_class = CreateStockSerializer
    #permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Stock.objects.all()



class UserDetailAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer


class UserDeleteAPIView(DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer

class SalesDeleteAPIView(DestroyAPIView):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer
        
class SalesDetailAPIView(generics.RetrieveAPIView):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer

class SalesCreateAPIView(generics.CreateAPIView):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer
    def perform_create(self, serializer):        
        serializer.save(user=self.request.user)

class SalesListAPIView(generics.ListAPIView):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer
class ProductListAPIView(generics.ListAPIView):
    #permission_classes = [IsAuthenticatedOrReadOnly]    
    pagination_class = PostLimitOffsetPagination
    serializer_class = ProductListSerializer

    def get_queryset(self, *args, **kwargs):        
        queryset_list = Product.objects.all().select_related()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(name__icontains=query)|
                Q(variants__sku__icontains=query)|
                Q(categories__name__icontains=query)
                ).distinct()
        return queryset_list
class SearchSkuListAPIView(generics.ListAPIView):
    pagination_class = PostLimitOffsetPagination
    serializer_class = ProductStockListSerializer
    def get_queryset(self, *args, **kwargs):        
        queryset_list = ProductVariant.objects.all().select_related()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                sku__startswith=query               
                ).distinct()
        return queryset_list
        
class ProductStockListAPIView(generics.ListAPIView):
    #permission_classes = [IsAuthenticatedOrReadOnly]    
    pagination_class = PostLimitOffsetPagination
    serializer_class = ProductStockListSerializer

    def get_queryset(self, *args, **kwargs):        
        queryset_list = ProductVariant.objects.all().select_related()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(sku__icontains=query) |
                Q(product__name__icontains=query)|
                Q(product__description__icontains=query)
                ).distinct()
        return queryset_list

class UserListAPIView(generics.ListAPIView):
    #permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = User.objects.all()
    serializer_class = UserListSerializer


# Permissions views
class PermissionListView(generics.ListAPIView):
    serializer_class = PermissionListSerializer
    queryset = Permission.objects.all()


class PermissionDetailAPIView(generics.RetrieveAPIView):
    serializer_class = PermissionListSerializer
    queryset = Permission.objects.all()


@api_view(['GET', 'POST'])
def snippet_list(request):
    if request.method == 'POST':
        serializer = CreateStockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)