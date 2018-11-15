# site settings rest api serializers
from decimal import Decimal
import datetime
from django.utils.formats import localize
from rest_framework import serializers
from saleor.countertransfer.models import CounterTransfer as Table
from saleor.countertransfer.models import CounterTransferItems as Item
from saleor.product.models import Stock

global fields, item_fields, module
module = 'counter_transfer_report'
fields = ('id',
          'name',
          'user',
          'counter',
          'created',
          'trashed',
          'date',
          'description')

item_fields = ('id',
               'stock',
               'sku',
               'qty',
               'transferred_qty',
               'expected_qty',
               'deficit',
               'sold',
               'tax',
               'discount',
               'price',
               'unit_price',
               'quantity',
               'counter',
               'closed',
               'trashed',
               'productName',
               'description',
               'product_category',)


class ItemsSerializer(serializers.ModelSerializer):
    sku = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    cost_price = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = item_fields + ('cost_price',)

    def get_cost_price(self, obj):
        try:
            return "{:,}".format(obj.stock.cost_price.gross)
        except:
            return ''

    def get_sku(self, obj):
        try:
            return obj.stock.variant.sku
        except:
            return ''

    def get_quantity(self, obj):
        try:
            return obj.stock.quantity
        except:
            return 0


def format_fields(fields_data, items_list):
    """
    Exclude supplied list of fields from global item list
    :param items_list: list type of fields to exclude
    :return:
    """
    # convert tuple to list
    temp = list(fields_data)
    # remove supplied fields
    for item in items_list:
        temp.remove(str(item))
    return tuple(temp)


class ItemsStockSerializer(serializers.ModelSerializer):
    sku = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    unit_cost = serializers.SerializerMethodField()  # price overrride (selling price)
    total_cost = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    counter = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = format_fields(item_fields, ['productName', 'price', 'unit_price']) + \
                 ('total_cost', 'product_name', 'unit_cost')

    def get_sku(self, obj):
        try:
            return obj.stock.variant.sku
        except:
            return ''

    def get_product_name(self, obj):
        return obj.productName

    def get_unit_cost(self, obj):
        try:
            return obj.stock.price_override.gross
        except:
            return obj.unit_price

    def get_total_cost(self, obj):
        try:
            return obj.price
        except:
            return 0

    def get_quantity(self, obj):
        try:
            return Item.objects.instance_quantities(obj.stock, filter_type='stock', counter=obj.counter)
        except:
            return 0

    def get_counter(self, obj):
        try:
            return {"id": obj.counter.id, "name": obj.counter.name}
        except:
            return None


class CloseTransferItemSerializer(serializers.ModelSerializer):
    close_details = serializers.JSONField(write_only=True)

    class Meta:
        model = Item
        fields = item_fields + ('close_details',)

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        instance.closed = True
        instance.qty = validated_data.get('qty', instance.qty)
        instance.deficit = validated_data.get('deficit', instance.deficit)
        # check if close json sent then close mark it as closed
        close_details = validated_data.pop('close_details')
        try:
            if close_details['store']:
                # return to stock
                if instance.qty > 0:
                    Stock.objects.increase_stock(instance.stock, instance.qty)
                    instance.price = Decimal(instance.sold * instance.unit_price)
                    instance.qty = 0
            else:
                # transfer to tomorrows stock
                tomorrow = datetime.timedelta(days=1) + datetime.date.today()
                counter = instance.counter
                query = Table.objects. \
                    filter(counter=instance.counter, date__icontains=tomorrow)
                if not query.exists():
                    new_transfer = Table.objects.create(date=tomorrow, counter=counter)
                else:
                    new_transfer = query.first()
                carry_items(new_transfer, [instance])

        except:
            pass
        instance.save()
        return instance


class UpdateTransferItemSerializer(serializers.ModelSerializer):
    close_details = serializers.JSONField(write_only=True)

    class Meta:
        model = Item
        fields = item_fields + ('close_details',)

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        instance.closed = False
        instance.price = validated_data.get('price', instance.price)
        # if edit qty is more than current qty reduce stock else decrease
        if int(validated_data.get('qty')) > instance.qty:
            diff = int(validated_data.get('qty')) - int(instance.qty)
            Stock.objects.decrease_stock(instance.stock, diff)
            instance.qty = validated_data.get('qty', instance.qty)
            instance.expected_qty = instance.qty
            instance.transferred_qty = int(instance.transferred_qty) + int(diff)
        elif int(validated_data.get('qty')) < instance.qty:
            diff = int(instance.qty) - int(validated_data.get('qty'))
            Stock.objects.increase_stock(instance.stock, diff)
            instance.qty = validated_data.get('qty', instance.qty)
            instance.expected_qty = instance.qty
            instance.transferred_qty = int(instance.transferred_qty) - int(diff)
        else:
            pass

        instance.save()
        return instance


class TableListSerializer(serializers.ModelSerializer):
    update_url = serializers.HyperlinkedIdentityField(view_name=module + ':api-update')
    update_items_url = serializers.HyperlinkedIdentityField(view_name=module + ':update')
    view_url = serializers.HyperlinkedIdentityField(view_name=module + ':update-view')
    text = serializers.SerializerMethodField()
    counter = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    counter_transfer_items = ItemsSerializer(many=True)
    quantity = serializers.SerializerMethodField()
    sold = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    worth = serializers.SerializerMethodField()
    all_item_closed = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = fields + (
            'quantity', 'sold', 'price', 'worth', 'all_item_closed',
            'counter_transfer_items', 'text',
            'view_url', 'update_url', 'update_items_url')

    def get_text(self, obj):
        try:
            return obj.name
        except:
            return ''

    def get_all_item_closed(self, obj):
        return obj.all_items_closed()

    def get_quantity(self, obj):
        return Item.objects.instance_quantities(obj)

    def get_sold(self, obj):
        return Item.objects.instance_sold_quantity(obj)

    def get_price(self, obj):
        return Item.objects.instance_sold_price(obj)

    def get_worth(self, obj):
        return "{:,}".format(Item.objects.instance_worth(obj))

    def get_date(self, obj):
        return localize(obj.date)

    def get_counter(self, obj):
        try:
            return {'id': obj.counter.id, 'name': obj.counter.name}
        except:
            return ''


def carry_items(instance, items):
    """
    Create new or update existing transferred stock items
    :param instance: model instance: Transfer instance
    :param items: dictionary: Stock item transferred
    :return:
    """
    for item in items:
        # if item exist, increase quantity else create
        try:
            item.stock = Stock.objects.get(pk=item.stock.pk)
        except Exception as e:
            print e
            pass
        query = Item.objects.filter(transfer=instance, stock=item.stock)
        if query.exists():
            print 'updating....'
            single = query.first()
            single.qty = int(single.qty) + int(item.qty)
            single.transferred_qty = int(single.transferred_qty) + int(item.qty)
            single.expected_qty = single.qty
            print single.transferred_qty
            single.price = Decimal(single.price) + Decimal(item.price)
            if single.qty > 0:
                single.save()
        else:
            single = Item()
            single.transfer = instance
            single.counter = instance.counter
            single.price = item.price
            single.unit_price = item.unit_price
            single.discount = item.discount
            single.tax = item.tax
            single.product_category = item.product_category
            single.productName = item.productName
            single.stock = item.stock
            single.qty = item.qty
            single.transferred_qty = single.qty
            single.expected_qty = single.qty
            single.sku = item.sku
            if single.qty > 0:
                single.save()

        # decrease stock
        # Stock.objects.decrease_stock(item['stock'], item['qty'])


def create_items(instance, items):
    """
    Create new or update existing transferred stock items
    :param instance: model instance: Transfer instance
    :param items: dictionary: Stock item transferred
    :return:
    """
    for item in items:
        # if item exist, increase quantity else create
        try:
            item['stock'] = Stock.objects.get(pk=item['stock'])
        except Exception as e:
            print e
            pass
        query = Item.objects.filter(transfer=instance, stock=item['stock'])
        if query.exists():
            print 'updating....'
            single = query.first()
            single.qty = int(single.qty) + int(item['qty'])
            single.transferred_qty = int(single.transferred_qty) + int(item['qty'])
            single.expected_qty = single.qty
            single.price = Decimal(single.price) + Decimal(item['price'])
            if single.qty > 0:
                single.save()
        else:
            single = Item()
            single.transfer = instance
            single.counter = instance.counter
            single.price = item['price']
            single.unit_price = item['price_override']
            single.discount = item['discount']
            single.tax = item['tax']
            single.product_category = item['product_category']
            single.productName = item['productName']
            single.stock = item['stock']
            single.qty = item['qty']
            single.transferred_qty = single.qty
            single.expected_qty = single.qty
            single.sku = item['sku']
            if single.qty > 0:
                single.save()

        # decrease stock
        Stock.objects.decrease_stock(item['stock'], item['qty'])


class CreateListSerializer(serializers.ModelSerializer):
    # counter_transfer_items = ItemsSerializer(many=True)
    counter_transfer_items = serializers.JSONField(write_only=True)

    class Meta:
        model = Table
        fields = fields + ('counter_transfer_items',)

    def create(self, validated_data):
        instance = Table()
        instance.name = validated_data.get('name')
        instance.counter = validated_data.get('counter')
        instance.date = validated_data.get('date')
        if validated_data.get('description'):
            instance.description = validated_data.get('description')
        counter_transfer_items = validated_data.pop('counter_transfer_items')

        # check if transfer with counter/date exists
        query = Table.objects. \
            filter(counter=instance.counter, date__icontains=instance.date)
        # if true update transferred items quantity and price
        # else save new instance and add items
        if not query.exists():
            instance.save()
        else:
            instance = query.first()

        create_items(instance, counter_transfer_items)

        return instance


class UpdateSerializer(serializers.ModelSerializer):
    items = serializers.JSONField(write_only=True)

    class Meta:
        model = Table
        fields = ('id', 'date', 'action', 'items',)

    def update(self, instance, validated_data):
        # action 1: carry forward 2: return to stock
        # tomorrow = datetime.timedelta(days=1) + datetime.date.today()
        action = validated_data.get('action')
        date = validated_data.pop('date')
        items = validated_data.pop('items')
        for cart in items:
            item = Item.objects.get(pk=cart['id'])
            item.qty = cart['qty']
            item.description = cart['description']
            item.deficit = cart['deficit']
            if action == 2:
                # return to stock
                if item.qty:
                    Stock.objects.increase_stock(item.stock, item.qty)
                    item.price = Decimal(item.sold * item.unit_price)
                    item.qty = 0
            else:
                # carry forward
                # transfer to tomorrows stock
                query = Table.objects. \
                    filter(counter=instance.counter, date__icontains=date)
                if not query.exists():
                    new_transfer = Table.objects.create(date=date, counter=instance.counter)
                else:
                    new_transfer = query.first()
                carry_items(new_transfer, [item])
                item.qty = 0

            if not item.closed:
                item.closed = True
                item.save()
        instance.save()
        return instance


class SnippetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    series = serializers.SerializerMethodField()
    categories = serializers.JSONField(required=False)

    def get_series(self, obj):
        return obj
    # total = serializers.IntegerField()
    # counter = serializers.CharField()
