from rest_framework.serializers import (   
    BooleanField,
    EmailField,
    DictField,
    CharField,
    ModelField,
    ModelSerializer,
    HyperlinkedIdentityField,
    SerializerMethodField,
    ValidationError
    )
from django.contrib.auth.models import Permission
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...discount.models import Sale
from ...sale.models import (Sales, SoldItem)
from ...order.models import (
    Order,
    DeliveryGroup,
    OrderedItem,
    )
from ...product.models import (
    Product,
    ProductVariant,
    Stock,
    )

User = get_user_model()

class CreateStockSerializer(ModelSerializer):
    class Meta:
        model = Stock
        exclude = ['quantity_allocated']


class UserCreateSerializer(ModelSerializer):
    email    = EmailField(label='Email address')    
    class Meta:
        model = User
        fields = [            
            'email',
            'password',  
            'is_staff',            
        ]
        extra_kwargs = {'password':
                            {'write_only':True}
                        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id']

def jwt_response_payload_handler(token, user=None, request=None):
        return {
            'token': token,
            'user': UserSerializer(user, context={'request': request}).data
        }


class UserListSerializer(serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='product-api:detail')
    delete_url = HyperlinkedIdentityField(view_name='product-api:user-delete')
    #profile = ProfileSerializer(required=False, )
    class Meta:
        model = User
        fields = ('id',
                 'email', 
                 'url', 
                 'delete_url')
class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoldItem
        fields = ('order', 'sku', 'quantity')
class SalesSerializer(serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='product-api:sales-detail')
    delete_url = HyperlinkedIdentityField(view_name='product-api:sales-delete')
    
    solditems = TrackSerializer(many=True)
    class Meta:
        model = Sales
        fields = ('id','user','invoice_number','total_net','sub_total','solditems')
    def create(self,validated_data):
        solditems_data = validated_data.pop('solditems')        
        sales = Sales.objects.create(**validated_data)
        for solditem_data in solditems_data:
            SoldItem.objects.create(sales=sales,**solditem_data)
            stock = Stock.objects.get(variant__sku=solditem_data['sku'])
            if stock:
                Stock.objects.allocate_stock(stock, solditem_data['quantity'])        
        return sales

class OrderedItemSerializer(serializers.Serializer):
    quantity = serializers.CharField()
    sku = serializers.CharField()


class ProductListSerializer(serializers.ModelSerializer):    
    vat_tax = SerializerMethodField()
    item_price = SerializerMethodField()    
    class Meta:
        model = Product
        fields = (
            'id', 
            'name',
            'vat_tax',
            'item_price',
            'description',
           )
    def get_vat_tax(self, obj):
        if obj.product_tax:
            tax = obj.product_tax.tax
        else:
            tax = 0
        return tax
    def get_item_price(self,obj):
        item_price = obj.price.gross
        return item_price


class ProductStockListSerializer(serializers.ModelSerializer):    
    productName = SerializerMethodField()
    price = SerializerMethodField()
    quantity = SerializerMethodField()
    productlist = UserListSerializer(required=False)
    tax = SerializerMethodField()
    discount = SerializerMethodField()
    #description = SerializerMethodField()
    class Meta:        
        model = ProductVariant
        fields = (
            'id',
            'productName',
            'sku',
            'price',
            'tax',
            'productlist',
            'discount',
            'quantity',            
            )
    def get_discount(self,obj):
        price = obj.get_price_per_item().gross
        try:
            discount = Sale.objects.get(products__pk=obj.product.pk)
            if discount.type == 'fixed':                
                discount = float(discount.value)/float(price)*float(100)
            else:
                discount = discount.value
        except:
            discount = 0
        discount = float(discount)*float(price)/float(100)
        return discount

    def get_quantity(self,obj):
        quantity = obj.get_stock_quantity()
        return quantity
    def get_productName(self,obj):
        productName = obj.display_product()
        return productName
    # def get_description(self,obj):
    #     return self.products.description
    def get_price(self,obj):
        price = obj.get_price_per_item().gross
        return price
    def get_tax(self,obj):
        if obj.product.product_tax:
            tax = obj.product.product_tax.tax
        else:
            tax = 0        
        return tax



class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant         



# PERMISSIONS SERIALIZERS
class PermissionListSerializer(serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='users-api:permission-detail')
    class Meta:
        model = Permission
        fields = ('id','url','codename')


