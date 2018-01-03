# table rest api serializers

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...product.models import ProductAttribute as Table
User = get_user_model()


class TableListSerializer(serializers.ModelSerializer):
    list_url = serializers.HyperlinkedIdentityField(view_name='sale-api:list-sold-items')

    class Meta:
        model = Table
        fields = ('id',
                  'name',
                  'list_url',
                 )
