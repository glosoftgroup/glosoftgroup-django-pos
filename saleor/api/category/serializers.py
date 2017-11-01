# category rest api serializers

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...product.models import Category, ProductVariant
from rest_framework.serializers import (
                HyperlinkedIdentityField,
                SerializerMethodField,
                )
User = get_user_model()


class CategoryListSerializer(serializers.ModelSerializer):
    product_variants_url = HyperlinkedIdentityField(view_name='variant-api:api-variant-list')
    total_products = SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id',
                  'name',
                  'description',
                  'product_variants_url',
                  'total_products',)

    def get_total_products(self, obj):
        return len(ProductVariant.objects.filter(product__categories__pk=obj.pk))