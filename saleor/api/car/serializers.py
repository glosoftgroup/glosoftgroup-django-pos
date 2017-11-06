from rest_framework import serializers
from ...car.models import Car as Table


class TableListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = (
                 'id',
                 'name',
                 'number')