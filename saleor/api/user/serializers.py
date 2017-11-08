from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    stock_allocated_url = serializers.HyperlinkedIdentityField(view_name='allocate-api:search-agent-allocate')

    class Meta:
        model = User
        fields = (
                 'id',
                 'name',
                 'email',
                 'mobile',
                 'stock_allocated_url',
                 )