# Payment rest api serializers

from rest_framework.fields import CurrentUserDefault
from rest_framework import serializers
from rest_framework.serializers import (
					SerializerMethodField,
					ValidationError,
				 )

from django.contrib.auth import get_user_model
User = get_user_model()
from ...sale.models import DrawerCash

class UserAuthenticationSerializer(serializers.ModelSerializer):
	email = serializers.EmailField()
	password = serializers.CharField(max_length=200)
	User = serializers.IntegerField()

	class Meta:
		model = DrawerCash
		fields = ('id',
				  'email',
				  'password',
				  'amount',
				  'terminal',
				  'User',
				  'manager',
				  'trans_type')
 	
	def validate_email(self, value):
		data = self.get_initial()
		email = data.get('email')
		user_qs = User.objects.filter(email=email)
		if not user_qs.exists():
			raise ValidationError('Email does not exist!')
		return value

	def validate_password(self,value):
		data = self.get_initial()
		password = data.get('password')
		email = data.get('email')		
		user = get_user_model().objects.get(email=email)
		if user.check_password(password):
			self.manager = user			
		else:
			raise ValidationError('Password failed!')
		return value

	def validate_User(self,value):
		data = self.get_initial()
		user = data.get('User')
		self.user = User.objects.get(pk=int(user))
		return value

	def create(self, validated_data):
		""" authenticate user
		"""			
		manager = self.manager
		terminal = validated_data['terminal']
		amount = validated_data['amount']
		cashier = serializers.CurrentUserDefault()
		user = validated_data['User']	
		drawer = DrawerCash.objects.create(manager=manager,										   
										   user = User.objects.get(pk=int(user)),
										   terminal=terminal,
										   amount=amount)
		print drawer		
		return validated_data
		
			
			
		



