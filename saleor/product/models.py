from __future__ import unicode_literals

import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import HStoreField
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.timezone import now
from django.db.models import F, Max, Q, Sum
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.text import slugify
from django.utils.translation import pgettext_lazy
from django.utils import six
from django_prices.models import PriceField
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from prices import PriceRange
from satchless.item import InsufficientStock, Item, ItemRange
from text_unidecode import unidecode
from versatileimagefield.fields import VersatileImageField, PPOIField

from ..discount.models import calculate_discounted_price
from ..supplier.models import Supplier
from ..search import index
from saleor.payment.models import PaymentOption
from .utils import get_attributes_display_map
from . import Status


@python_2_unicode_compatible
class Category(MPTTModel):
    name = models.CharField(
        pgettext_lazy('Category field', 'name'), max_length=128,unique=True)
    slug = models.SlugField(
        pgettext_lazy('Category field', 'slug'), max_length=50)
    description = models.TextField(
        pgettext_lazy('Category field', 'description'), blank=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children',
        verbose_name=pgettext_lazy('Category field', 'parent'))
    hidden = models.BooleanField(
        pgettext_lazy('Category field', 'hidden'), default=False)

    objects = models.Manager()
    tree = TreeManager()

    class Meta:
        verbose_name = pgettext_lazy('Category model', 'category')
        verbose_name_plural = pgettext_lazy('Category model', 'categories')
        app_label = 'product'

    def __str__(self):
        return self.name

    def get_product_num(self):
        return len(self.products.all())

    def get_absolute_url(self, ancestors=None):
        return reverse('product:category',
                       kwargs={'path': self.get_full_path(ancestors),
                               'category_id': self.id})

    def get_full_path(self, ancestors=None):
        if not self.parent_id:
            return self.slug
        if not ancestors:
            ancestors = self.get_ancestors()
        nodes = [node for node in ancestors] + [self]
        return '/'.join([node.slug for node in nodes])

    def set_hidden_descendants(self, hidden):
        self.get_descendants().update(hidden=hidden)


@python_2_unicode_compatible
class ProductClass(models.Model):
    name = models.CharField(
        pgettext_lazy('Product class field', 'name'), max_length=128, unique=True)
    has_variants = models.BooleanField(
        pgettext_lazy('Product class field', 'has variants'), default=True)
    product_attributes = models.ManyToManyField(
        'ProductAttribute', related_name='products_class', blank=True,
        verbose_name=pgettext_lazy('Product class field',
                                   'product attributes'))
    variant_attributes = models.ManyToManyField(
        'ProductAttribute', related_name='product_variants_class', blank=True,
        verbose_name=pgettext_lazy('Product class field', 'variant attributes'))
    is_shipping_required = models.BooleanField(
        pgettext_lazy('Product class field', 'is shipping required'),
        default=False)

    class Meta:
        verbose_name = pgettext_lazy(
            'Product class model', 'product class')
        verbose_name_plural = pgettext_lazy(
            'Product class model', 'product classes')
        app_label = 'product'

    def __str__(self):
        return self.name

    def __repr__(self):
        class_ = type(self)
        return '<%s.%s(pk=%r, name=%r)>' % (
            class_.__module__, class_.__name__, self.pk, self.name)


class ProductTax(models.Model):    
    tax_name = models.CharField(
        pgettext_lazy('Tax name', 'Tax name (optional)'),
        max_length=128, blank=True)   
    tax_label = models.CharField(
        pgettext_lazy('Label on invoices', 'Short text printed on invoices'),
        max_length=128, blank=True)
    tax = models.IntegerField(pgettext_lazy('Product Tax', 'tax %'),
        validators=[MinValueValidator(0)], unique=True, default=Decimal(0))

    def __str__(self):
        return self.tax_name + ' ' + str(self.tax)+' %'

    def get_tax(self):
        return self.tax


class ProductManager(models.Manager):

    def get_available_products(self):
        today = datetime.date.today()
        return self.get_queryset().filter(
            Q(available_on__lte=today) | Q(available_on__isnull=True))


@python_2_unicode_compatible
class Product(models.Model, ItemRange, index.Indexed):
    product_class = models.ForeignKey(
        ProductClass, related_name='products',
        verbose_name=pgettext_lazy('Product field', 'product class'))
    product_tax = models.ForeignKey(
        ProductTax, related_name='producttax',blank=True, null=True,
        verbose_name=pgettext_lazy('Product field', 'product class'))
    name = models.CharField(
        pgettext_lazy('Product field', 'name'),unique=True, max_length=128)
    description = models.TextField(
        verbose_name=pgettext_lazy('Product field', 'description'), blank=True, null=True)
    categories = models.ManyToManyField(
        Category, verbose_name=pgettext_lazy('Product field', 'categories'),
        related_name='products')
    price = PriceField(
        pgettext_lazy('Product field', 'price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12,
        validators=[MinValueValidator(0)], default=Decimal(0), decimal_places=2)
    minimum_price = PriceField(
        pgettext_lazy('Product variant field', 'minimum price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)
    wholesale_price = PriceField(
        pgettext_lazy('Product field', 'Wholesale price'),
        currency=settings.DEFAULT_CURRENCY, blank=True,null=True, max_digits=12, decimal_places=2)
    product_supplier = models.ForeignKey(
        Supplier, related_name='suppliers', blank=True, null=True,
        verbose_name=pgettext_lazy('Product field', 'product supplier'))
    
    available_on = models.DateField(
        pgettext_lazy('Product field', 'available on'), blank=True, null=True)
    attributes = HStoreField(pgettext_lazy('Product field', 'attributes'),
                             default={})
    updated_at = models.DateTimeField(
        pgettext_lazy('Product field', 'updated at'), auto_now=True, null=True)
    is_featured = models.BooleanField(
        pgettext_lazy('Product field', 'is featured'), default=False)
    low_stock_threshold = models.IntegerField(
        pgettext_lazy('Product field', 'low stock threshold'),
        validators=[MinValueValidator(0)], null=True,blank=True, default=Decimal(10))
    

    objects = ProductManager()

    search_fields = [
        index.SearchField('name', partial_match=True),
        index.SearchField('description'),
        index.FilterField('available_on')]

    class Meta:
        app_label = 'product'
        verbose_name = pgettext_lazy('Product model', 'product')
        verbose_name_plural = pgettext_lazy('Product model', 'products')

    def __iter__(self):
        if not hasattr(self, '__variants'):
            setattr(self, '__variants', self.variants.all())
        return iter(getattr(self, '__variants'))

    def __repr__(self):
        class_ = type(self)
        return '<%s.%s(pk=%r, name=%r)>' % (
            class_.__module__, class_.__name__, self.pk, self.name)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product:details', kwargs={'slug': self.get_slug(),
                                                  'product_id': self.id})

    def get_slug(self):
        return slugify(smart_text(unidecode(self.name)))
    
    def get_product_tax(self):
        return self.product_tax

    def get_tax_value(self):
        return self.product_tax.get_tax()

    def is_in_stock(self):
        return any(variant.is_in_stock() for variant in self)

    def total_stock(self):
        return Sum(self.variant.stock.stock_available())

    def total_variants(self):
        return len(self.variants.all())

    def get_first_category(self):
        for category in self.categories.all().order_by('id'):
            if not category.hidden:
                return category
        return None

    def get_variants_count(self):
        variants = self.variants.filter(product=self.pk)
        total = 0
        for stock in variants:
            total += stock.get_stock_quantity()
        return total

    def is_available(self):
        today = datetime.date.today()
        return self.available_on is None or self.available_on <= today

    def get_first_image(self):
        first_image = self.images.first()

        if first_image:
            return first_image.image
        return None

    def get_attribute(self, pk):
        return self.attributes.get(smart_text(pk))

    def set_attribute(self, pk, value_pk):
        self.attributes[smart_text(pk)] = smart_text(value_pk)

    def get_price_range(self, discounts=None,  **kwargs):
        if not self.variants.exists():
            price = calculate_discounted_price(self, self.price, discounts,
                                               **kwargs)
            return PriceRange(price, price)
        else:
            return super(Product, self).get_price_range(
                discounts=discounts, **kwargs)


class ProductVariantManager(models.Manager):

    def get_low_stock(self):
        today = datetime.date.today()
        return self.get_queryset().filter(stock__quantity__lte=F('low_stock_threshold'))

    def get_in_stock(self):
        today = datetime.date.today()
        return self.get_queryset().filter(stock__quantity__gte=1)


@python_2_unicode_compatible
class ProductVariant(models.Model, Item):
    sku = models.CharField(
        pgettext_lazy('Product variant field', 'SKU'), max_length=32, unique=True)
    name = models.CharField(
        pgettext_lazy('Product variant field', 'variant name'), max_length=100,
        blank=True)
    variant_supplier = models.ForeignKey(
        Supplier, related_name='variant_supplier', blank=True, null=True,
        verbose_name=pgettext_lazy('Product variant field', 'product variant supplier'))
    
    product = models.ForeignKey(Product, related_name='variants')
    attributes = HStoreField(
        pgettext_lazy('Product variant field', 'attributes'), default={})
    images = models.ManyToManyField(
        'ProductImage', through='VariantImage',
        verbose_name=pgettext_lazy('Product variant field', 'images'))
    low_stock_threshold = models.IntegerField(
        pgettext_lazy('Product variant field', 'low stock threshold'),
        validators=[MinValueValidator(0)], null=True,blank=True, default=Decimal(10))
    objects = ProductVariantManager()
    
    class Meta:
        app_label = 'product'
        verbose_name = pgettext_lazy('Product variant model', 'product variant')
        verbose_name_plural = pgettext_lazy('Product variant model', 'product variants')

    def __str__(self):
        return self.name or self.display_variant()

    def check_quantity(self, quantity):
        available_quantity = self.get_stock_quantity()
        if quantity > available_quantity:
            raise InsufficientStock(self)

    def get_stock_pk(self):
        stock_pk = self.stock.all().values('pk')
        if stock_pk.exists():
            for st in stock_pk:
                stock_pk = st['pk']
        else:
            stock_pk = 0        
        return stock_pk

    def get_stock_quantity(self):
        quantity = self.stock.filter(quantity__gte=1).aggregate(Sum('quantity'))['quantity__sum']
        if quantity:
            return quantity
        else:
            return 0

    def get_stock_quantity_single(self):
        # if not len(self.stock.all()):
        #     return 0
        # return max([stock.quantity_available for stock in self.stock.all()])
        checker = True
        quantity = 0
        try:
            while checker:
                quantity = self.stock.all().first().quantity
                if quantity > 0:
                    quantity = self.stock.all().first().quantity
                    checker = False
                else:
                    self.stock.all().first().delete()
            return quantity
        except:
            return quantity

    def get_min_price_per_item(self):
        # return self.minimum_price or self.product.minimum_price
        checker = True
        price = 0
        try:
            while checker:
                stock = self.stock.all().first().quantity
                if stock > 0:
                    price = self.stock.all().first().minimum_price
                    checker = False
                else:
                    self.stock.all().first().delete()
            return price
        except Exception as e:
            return price

    def get_price_per_item(self, discounts=None, **kwargs):
        checker = True
        price = 0
        try:
            while checker:
                stock = self.stock.all().first().quantity
                if stock > 0:
                    price = self.stock.all().first().price_override
                    checker = False
                else:
                    self.stock.all().first().delete()
            price = calculate_discounted_price(self.product, price, discounts,
                                               **kwargs)
            return price
        except Exception as e:
            return price

    def get_wholesale_price_per_item(self, discounts=None, **kwargs):
        checker = True
        price = 0
        try:
            while checker:
                quantity = self.stock.all().first().quantity
                if quantity > 0:
                    price = self.stock.all().first().wholesale_override
                    checker = False
                else:
                    self.stock.all().first().delete()
            price = calculate_discounted_price(self.product, price, discounts,
                                               **kwargs)
            return price
        except Exception as e:
            return price

    def get_total_price_cost(self):
        cost = self.get_cost_price() * self.get_stock_quantity()
        return cost

    def get_absolute_url(self):
        slug = self.product.get_slug()
        product_id = self.product.id
        return reverse('product:details',
                       kwargs={'slug': slug, 'product_id': product_id})

    def as_data(self):
        return {
            'product_name': str(self),
            'product_id': self.product.pk,
            'variant_id': self.pk,
            'unit_price': str(self.get_price_per_item().gross)}

    def is_shipping_required(self):
        return self.product.product_class.is_shipping_required

    def get_stock_cost_price(self):
        checker = True
        price = 0
        try:
            while checker:
                quantity = self.stock.all().first().quantity
                if quantity > 0:
                    price = self.stock.all().first().cost_price.gross
                    checker = False
                else:
                    self.stock.all().first().delete()
            return price
        except Exception as e:
            return price


    def is_in_stock(self):
        return any(
            [stock.quantity_available > 0 for stock in self.stock.all()])

    def get_attribute(self, pk):
        return self.attributes.get(smart_text(pk))

    def set_attribute(self, pk, value_pk):
        self.attributes[smart_text(pk)] = smart_text(value_pk)

    def display_variant(self, attributes=None):
        if attributes is None:
            attributes = self.product.product_class.variant_attributes.all()
        values = get_attributes_display_map(self, attributes)
        if values:
            return ', '.join(
                [' %s' % ( smart_text(value))
                 for (key, value) in six.iteritems(values)])            
        else:
            return smart_text(self.sku)

    def display_product(self):
        return '%s (%s)' % (smart_text(self.product),
                            smart_text(self))

    def get_first_image(self):
        return self.product.get_first_image()

    def select_stockrecord(self, quantity=1):
        # By default selects stock with lowest cost price
        stock = filter(
            lambda stock: stock.quantity_available >= quantity,
            self.stock.all())
        stock = sorted(stock, key=lambda stock: stock.cost_price, reverse=True)
        if stock:
            return stock[0]

    def get_cost_price(self):
        stock = self.select_stockrecord()
        if stock:
            if stock.cost_price:
                return stock.cost_price
            else:
                return 0
        else:
            return 0

    def product_category(self):
        try:
            category = self.product.categories.first().name
            return category
        except:
            return ''


@python_2_unicode_compatible
class StockLocation(models.Model):
    DEFAULT_PK=1
    name = models.CharField(
        pgettext_lazy('Stock location field', 'location'), max_length=100)

    def __str__(self):
        return self.name


class StockManager(models.Manager):

    def allocate_stock(self, stock, quantity):
        stock.quantity_allocated = F('quantity_allocated') + quantity
        stock.save(update_fields=['quantity_allocated'])

    def deallocate_stock(self, stock, quantity):
        stock.quantity_allocated = F('quantity_allocated') - quantity
        stock.save(update_fields=['quantity_allocated'])

    def decrease_stock(self, stock, quantity):
        stock.quantity = F('quantity') - quantity
        stock.save(update_fields=['quantity', 'quantity_allocated'])

    def increase_stock(self, stock, quantity):
        stock.quantity = F('quantity') + quantity
        stock.save(update_fields=['quantity', 'quantity_allocated'])

    def get_low_stock(self, all_low_stock=True):
        """ all low stock of filter non notified stock only"""
        if all_low_stock:
            return self.get_queryset().filter(quantity__lte=F('low_stock_threshold'))
        else:
            return self.get_queryset().filter(quantity__lte=F('low_stock_threshold'))\
                .filter(notified=False)

    def get_credit_balance(self, supplier):
        return self.get_queryset().filter(variant__product__product_supplier=supplier).aggregate(total=Sum(F('total_cost') - F('amount_paid')))['total']

    def get_credit_total(self, supplier):
        return self.get_queryset().filter(variant__product__product_supplier=supplier).aggregate(total=Sum(F('total_cost')))['total']


@python_2_unicode_compatible
class Stock(models.Model):
    status = models.CharField(
        pgettext_lazy('Stock field', 'Credit status'),
        max_length=32, choices=Status.CHOICES, default=Status.PAYMENT_PENDING)
    variant = models.ForeignKey(
        ProductVariant, related_name='stock',
        verbose_name=pgettext_lazy('Stock item field', 'variant'))
    location = models.ForeignKey(StockLocation, default=StockLocation.DEFAULT_PK)
    quantity = models.IntegerField(
        pgettext_lazy('Stock item field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    low_stock_threshold = models.IntegerField(
        pgettext_lazy('Stock item field', 'low stock threshold'),
        validators=[MinValueValidator(0)], null=True, blank=True, default=Decimal(10))
    
    quantity_allocated = models.IntegerField(
        pgettext_lazy('Stock item field', 'allocated quantity'),
        validators=[MinValueValidator(0)], default=Decimal(0))
    cost_price = PriceField(
        pgettext_lazy('Stock item field', 'cost price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)
    amount_paid = PriceField(
        pgettext_lazy('Stock item field', 'cost price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)
    total_cost = PriceField(
        pgettext_lazy('Stock item field', 'total cost price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)
    price_override = PriceField(
        pgettext_lazy('Stock item field', 'price override'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)
    minimum_price = PriceField(
        pgettext_lazy('Stock item field', 'minimum price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)
    wholesale_override = PriceField(
        pgettext_lazy('Stock item field', 'wholesale override'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)

    created = models.DateTimeField(
        pgettext_lazy('Stock field', 'created'),
        default=now, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        verbose_name=pgettext_lazy('Stock history entry field', 'user'))
    comment = models.CharField(
        pgettext_lazy('Stock entry field', 'comment'),
        max_length=100, default='', blank=True)
    notified = models.BooleanField(default=False, blank=False)

    objects = StockManager()

    class Meta:
        app_label = 'product'
        # unique_together = ('variant', 'location')

    def __str__(self):
        return '%s - %s' % (self.variant.name, self.pk)

    @property
    def quantity_available(self):
        return max(self.quantity - self.quantity_allocated, 0)

    @property
    def cost_priceAsData(self):
        return self.cost_price

    def get_balance(self):
        try:
            return self.cost_price.gross - self.amount_paid.gross
        except:
            return 0

    @property
    def varaintName(self):
        return self.variant.price_override

    @property
    def Access_pk(self):
        return self.pk

    def get_total_credit(self):
        return Stock.objects.get_total_credit()

    def get_total_cost(self):
        try:
            return (self.cost_price.gross * self.quantity)
        except:
            return 0


@python_2_unicode_compatible
class StockCreditHistory(models.Model):
    date = models.DateTimeField(
        pgettext_lazy('Stock credit history entry field', 'last history change'),
        default=now, editable=False)
    stock = models.ForeignKey(
        Stock, related_name='credit_history',
        verbose_name=pgettext_lazy('Stock credit history entry field', 'order'))

    comment = models.CharField(
        pgettext_lazy('Stock history credit entry field', 'comment'),
        max_length=100, default='', blank=True)
    crud = models.CharField(
        pgettext_lazy('Stock history credit entry field', 'crud'),
        max_length=30, default='', blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        verbose_name=pgettext_lazy('Stock history credit entry field', 'user'))

    class Meta:
        ordering = ('date', )
        verbose_name = pgettext_lazy(
            'Stock history credit entry model', 'Stock credit history entry')
        verbose_name_plural = pgettext_lazy(
            'Stock history credit entry model', 'Stock credit history entries')

    def __str__(self):
        return pgettext_lazy(
            'Stock credit history entry str',
            'Stock credit HistoryEntry  for Stock #%d') % self.stock.pk


@python_2_unicode_compatible
class StockHistoryEntry(models.Model):
    date = models.DateTimeField(
        pgettext_lazy('Stock history entry field', 'last history change'),
        default=now, editable=False)
    stock = models.ForeignKey(
        Stock, related_name='history',
        verbose_name=pgettext_lazy('Stock history entry field', 'order'))

    comment = models.CharField(
        pgettext_lazy('Stock history entry field', 'comment'),
        max_length=100, default='', blank=True)
    crud = models.CharField(
        pgettext_lazy('Stock history entry field', 'crud'),
        max_length=30, default='', blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        verbose_name=pgettext_lazy('Stock history entry field', 'user'))

    class Meta:
        ordering = ('date', )
        verbose_name = pgettext_lazy(
            'Stock history entry model', 'Stock history entry')
        verbose_name_plural = pgettext_lazy(
            'Stock history entry model', 'Stock history entries')

    def __str__(self):
        return pgettext_lazy(
            'Stock history entry str',
            'StockHistoryEntry for Stock #%d') % self.stock.pk


@python_2_unicode_compatible
class ProductAttribute(models.Model):
    slug = models.SlugField(
        pgettext_lazy('Product attribute field', 'internal name'),
        max_length=50, unique=True)
    name = models.CharField(
        pgettext_lazy('Product attribute field', 'display name'),
        max_length=100,unique=True)

    class Meta:
        ordering = ('slug', )
        verbose_name = pgettext_lazy('Product attribute model', 'product attribute')
        verbose_name_plural = pgettext_lazy('Product attribute model', 'product attributes')

    def __str__(self):
        return self.name

    def get_formfield_name(self):
        return slugify('attribute-%s' % self.slug)

    def has_values(self):
        return self.values.exists()


@python_2_unicode_compatible
class VariantAttribute(models.Model):
    slug = models.SlugField(
        pgettext_lazy('Variant attribute field', 'internal name'),
        max_length=50, unique=True)
    name = models.CharField(
        pgettext_lazy('Variant attribute field', 'display name'),
        max_length=100,unique=True)

    class Meta:
        ordering = ('slug', )
        verbose_name = pgettext_lazy('Variant attribute model', 'variant attribute')
        verbose_name_plural = pgettext_lazy('Variant attribute model', 'variant attributes')

    def __str__(self):
        return self.name

    def get_formfield_name(self):
        return slugify('variant-attribute-%s' % self.slug)

    def has_values(self):
        return self.values.exists()


@python_2_unicode_compatible
class AttributeChoiceValue(models.Model):
    name = models.CharField(
        pgettext_lazy('Attribute choice value field', 'display name'),
        max_length=100)
    slug = models.SlugField()
    color = models.CharField(
        pgettext_lazy('Attribute choice value field', 'color'),
        max_length=7,
        validators=[RegexValidator('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')],
        blank=True)
    attribute = models.ForeignKey(ProductAttribute, related_name='values')

    class Meta:
        unique_together = ('name', 'attribute')
        verbose_name = pgettext_lazy(
            'Attribute choice value model',
            'attribute choices value')
        verbose_name_plural = pgettext_lazy(
            'Attribute choice value model',
            'attribute choices values')

    def __str__(self):
        return self.name


class ImageManager(models.Manager):
    def first(self):
        try:
            return self.get_queryset()[0]
        except IndexError:
            pass


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name='images',
        verbose_name=pgettext_lazy('Product image field', 'product'))
    image = VersatileImageField(
        upload_to='products', ppoi_field='ppoi', blank=False,
        verbose_name=pgettext_lazy('Product image field', 'image'))
    ppoi = PPOIField(verbose_name=pgettext_lazy('Product image field', 'ppoi'))
    alt = models.CharField(
        pgettext_lazy('Product image field', 'short description'),
        max_length=128, blank=True)
    order = models.PositiveIntegerField(
        pgettext_lazy('Product image field', 'order'),
        editable=False)

    objects = ImageManager()

    class Meta:
        ordering = ('order', )
        app_label = 'product'
        verbose_name = pgettext_lazy('Product image model', 'product image')
        verbose_name_plural = pgettext_lazy('Product image model', 'product images')

    def get_ordering_queryset(self):
        return self.product.images.all()

    def save(self, *args, **kwargs):
        if self.order is None:
            qs = self.get_ordering_queryset()
            existing_max = qs.aggregate(Max('order'))
            existing_max = existing_max.get('order__max')
            self.order = 0 if existing_max is None else existing_max + 1
        super(ProductImage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        qs = self.get_ordering_queryset()
        qs.filter(order__gt=self.order).update(order=F('order') - 1)
        super(ProductImage, self).delete(*args, **kwargs)


class VariantImage(models.Model):
    variant = models.ForeignKey(
        'ProductVariant', related_name='variant_images',
        verbose_name=pgettext_lazy('Variant image field', 'variant'))
    image = models.ForeignKey(
        ProductImage, related_name='variant_images',
        verbose_name=pgettext_lazy('Variant image field', 'image'))

    class Meta:
        verbose_name = pgettext_lazy(
            'Variant image model', 'variant image')
        verbose_name_plural = pgettext_lazy('Variant image model', 'variant images')


def get_supplier_credit_balance(supplier=None):
    return Stock.objects.get_credit_balance(supplier)


def get_supplier_credit_total(supplier=None):
    return Stock.objects.get_credit_total(supplier)