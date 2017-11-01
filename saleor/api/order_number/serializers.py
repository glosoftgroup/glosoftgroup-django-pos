from rest_framework import serializers


class OrderNumberSerializer(serializers.Serializer):
    number = serializers.CharField(max_length=200)
