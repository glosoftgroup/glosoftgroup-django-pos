# Payment rest api serializers

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import (
                    SerializerMethodField,
                    ValidationError,                    
                 )

from django.contrib.auth import get_user_model
User = get_user_model()
from ...discount.models import Sale
from ...customer.models import Customer
from ...decorators import user_trail

class CustomerDiscountListSerializer(serializers.ModelSerializer):
    discounts = SerializerMethodField()
    class Meta:
        model = Customer
        fields = ('id',
                 'name',
                 'discounts'
                 )
    def get_discounts(self,obj):
        discounts = {}
        l=[]
        dis = obj.customer_discount.all()
        for discount in dis:           
            value = discount.value
            name = discount.name
            for variant in discount.variant.all():
                discounts={'id':variant.id,'name':name,'value':value}
                l.append(discounts)
        return l



class DiscountListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = ('id',
                 'name',
                 'value',
                 'type',
                 'variant',
                 'customers')