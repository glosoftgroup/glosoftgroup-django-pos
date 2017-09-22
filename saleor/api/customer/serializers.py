from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import (
					SerializerMethodField,
					ValidationError,					
				 )

from django.contrib.auth import get_user_model
User = get_user_model()
from ...customer.models import Customer
from ...decorators import user_trail

class CustomerListSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Customer
        fields = ('id',
        	     'name',
                 'email',                 
                 'mobile',
                 'loyalty_points',
                 'redeemed_loyalty_points'
                 )


class CreditWorthyCustomerSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Customer
        fields = ('id',
                 'name',
                 'mobile')


class CustomerUpdateSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Customer
        fields = ('id',
        	     'name',
                 'email',                 
                 'mobile',
                 'loyalty_points',                 
                 )

    def validate_loyalty_points(self,value):        
        data = self.get_initial()
        self.points = data.get('loyalty_points')
        try:
        	print Decimal(self.points)
        except:
        	raise ValidationError('Invalid loyalty points')
    
    def update(self, instance, validated_data):          
    	# points = validated_data.get('loyalty_points')      
    	# print points
    	instance.loyalty_points -= Decimal(self.points)
    	instance.redeemed_loyalty_points += Decimal(self.points)
    	instance.save()
        #redeem = Customer.objects.redeem_points(instance,points)        
        return instance