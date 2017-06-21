# Payment rest api serializers
from rest_framework import serializers

from ...payment.models import MpesaPayment


class MpesaPaymentListSerializer(serializers.ModelSerializer):
	#url = HyperlinkedIdentityField(view_name='product-api:detail')	
	class Meta:
		model = MpesaPayment
		fields = ('id',
				 'ref_number', 
				 'phone', 
				 'first_name',
				 'middle_name',
				 'last_name')


