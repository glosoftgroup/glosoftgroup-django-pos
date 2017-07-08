from django.conf import settings
from datetime import date
from rest_framework.serializers import (
				ModelSerializer,
				HyperlinkedIdentityField,
				SerializerMethodField,
				ValidationError,
				)

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...discount.models import Sale
from ...discount.models import get_product_discounts
from ...sale.models import (
			Sales, 
			SoldItem,
			Terminal)
from ...site.models import SiteSettings
from ...product.models import (
			Product,
			ProductVariant,
			Stock,
			)
from decimal import Decimal
from ...customer.models import Customer


User = get_user_model()


class CreateStockSerializer(ModelSerializer):
	class Meta:
		 model = Stock
		 exclude = ['quantity_allocated']


class CustomerListSerializer(serializers.ModelSerializer):
	url = HyperlinkedIdentityField(view_name='product-api:detail')
	class Meta:
		model = Customer
		fields = ('id',
				 'email', 
				 'url',
				 'nid',
				 )


class TrackSerializer(serializers.ModelSerializer):
	class Meta:
		model = SoldItem
		fields = (
				'order',
				'sku',
				'quantity',
				'unit_cost',
				'total_cost',
				'product_name',
				'product_category'
				 )


class SalesSerializer(serializers.ModelSerializer):
	url = HyperlinkedIdentityField(view_name='product-api:sales-details')
	solditems = TrackSerializer(many=True)
	class Meta:
		model = Sales
		fields = ('id',
				 'user',
				 'invoice_number',
				 'total_net',
				 'sub_total',                 
				 'url',
				 'balance',
				 'terminal',
				 'amount_paid',
				 'solditems',
				 'customer',
				)

	def validate_terminal(self,value):
		data = self.get_initial()
		self.terminal_id = int(data.get('terminal'))
		self.l=[]
		terminals = Terminal.objects.all()
		for term in terminals:
			self.l.append(term.pk)
		if not self.terminal_id in self.l:		
			raise ValidationError('Terminal specified does not extist')
		return value	

	def create(self,validated_data):
		# add sold amount to drawer	
		total_net = Decimal(validated_data.get('total_net'))
		terminal = Terminal.objects.get(pk=self.terminal_id)	
		terminal.amount += Decimal(total_net)		
		terminal.save()		
		# calculate loyalty_points
		customer = validated_data.get('customer')		
		invoice_number = validated_data.get('invoice_number')
		if customer:
			total_net = validated_data.get('total_net')
			points_eq = SiteSettings.objects.get(pk=1)		
			points_eq = points_eq.loyalty_point_equiv #settings.LOYALTY_POINT_EQUIVALENCE
			loyalty_points = total_net/points_eq			
			customer.loyalty_points += loyalty_points
			customer.save()
		# get sold products	
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
	tax = SerializerMethodField()
	discount = SerializerMethodField()
	product_category = SerializerMethodField()
	#description = SerializerMethodField()
	class Meta:        
		model = ProductVariant
		fields = (
			'id',
			'productName',
			'sku',
			'price',
			'tax',
			'discount',
			'quantity',
			'product_category',            
			)

	def get_discount(self,obj):
		today = date.today()
		price = obj.get_price_per_item().gross		
		discounts = Sale.objects.filter(start_date__lte=today).filter(end_date__gte=today)
		discount = 0
		discount_list = get_product_discounts(obj.product, discounts)
		for discount in discount_list:
			try:
				discount = discount.factor
			except:
				discount = discount.amount.gross
				discount = Decimal(discount)/Decimal(price)*Decimal(100)

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

	def get_product_category(self,obj):
		product_category = obj.product_category()
		return product_category


class ProductVariantSerializer(serializers.ModelSerializer):
	class Meta:
		model = ProductVariant


class UserSerializer(serializers.ModelSerializer):
	# used during jwt authentication
	class Meta:
		model = User
		fields = ['id','email','name']