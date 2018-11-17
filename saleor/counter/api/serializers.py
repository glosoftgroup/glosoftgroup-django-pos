# site settings rest api serializers

from rest_framework import serializers
from saleor.counter.models import Counter as Table


class TableListSerializer(serializers.ModelSerializer):
    update_url = serializers.HyperlinkedIdentityField(view_name='counter:api-update')
    delete_url = serializers.HyperlinkedIdentityField(view_name='counter:api-delete')
    text = serializers.SerializerMethodField()
    is_closed = serializers.SerializerMethodField()
    last_open = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = ('id',
                  'name',
                  'text',
                  'is_closed',
                  'last_open',
                  'description',
                  'update_url',
                  'delete_url'
                 )

    def get_text(self, obj):
        try:
            return obj.name
        except:
            return ''

    def get_is_closed(self, obj):
        return obj.is_closed()

    def get_last_open(self, obj):
        return obj.last_open()


class CreateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ('id',
                  'name',
                  'description',
                 )

    def create(self, validated_data):
        instance = Table()
        instance.name = validated_data.get('name')
        if validated_data.get('description'):
            instance.description = validated_data.get('description')
        instance.save()

        return instance


class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ('id',
                  'name',
                  'description',
                 )

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)

        instance.save()
        return instance
