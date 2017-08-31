# Payment rest api serializers
from rest_framework import serializers
from rest_framework.serializers import (
					SerializerMethodField,
					IntegerField
				 )
from datetime import datetime
from ...sale.models import PaymentOption
from ...payment.models import MpesaPayment

class MpesaPaymentUpdateSerializer(serializers.ModelSerializer):
	status = IntegerField(max_value=1, min_value=0)
	class Meta:
		model = MpesaPayment
		fields = ('id',
				 'ref_number',
				 'status'
				 )

	def update(self, instance, validated_data):
	   
		instance.id = validated_data.get('id', instance.id)
		instance.status = validated_data.get('status', instance.status)
		instance.save()

		return instance

class MpesaPaymentListSerializer(serializers.ModelSerializer):
	time = SerializerMethodField()
	class Meta:
		model = MpesaPayment
		fields = ('id',
				 'ref_number', 
				 'phone',
				 'amount', 
				 'first_name',
				 'middle_name',
				 'last_name',
				 'time',
				 'status')
	def get_time(self,obj):
		time = obj.created.strftime("%d/%m/%Y %H:%M:%S %p")
		return time

class PaymentOptionListSerializer(serializers.ModelSerializer):	
	class Meta:
		model = PaymentOption
		fields = ('id',
				 'name', 
				 'description',)

				 