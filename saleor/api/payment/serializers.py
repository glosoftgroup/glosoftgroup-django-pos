# Payment rest api serializers
from rest_framework import serializers
from rest_framework.serializers import (
					SerializerMethodField,
				 )
from datetime import datetime
from ...payment.models import MpesaPayment


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
				 'time')
	def get_time(self,obj):
		time = obj.created.strftime("%d/%m/%Y %H:%M:%S %p")
		return time

