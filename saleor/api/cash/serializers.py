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
from ...sale.models import DrawerCash
from ...decorators import user_trail

class UserAuthorizationSerializer(serializers.Serializer):
	email = serializers.EmailField()
	password = serializers.CharField(max_length=200)
	user = serializers.CharField(max_length=200)
	terminal = serializers.CharField(max_length=200)

	def validate_email(self, value):
		data = self.get_initial()
		email = data.get('email')		
		self.l=[]
		user_qs = get_user_model().objects.all()
		for user in user_qs:
			self.l.append(user.email)
		if not email in self.l:		
			raise PermissionDenied('Authentication Failed!')
		else:
			self.user = get_user_model().objects.get(email=email)
		return value

	def validate_password(self,value):
		data = self.get_initial()
		password = data.get('password')
		email = data.get('email')
		if not email in self.l:		
			return value #raise ValidationError('Email does not exist!')
		else:
			self.user = get_user_model().objects.get(email=email)
				
			if self.user.check_password(password) and self.user.has_perm('sales.make_sale'):
				self.manager = self.user			
			else:
				raise PermissionDenied('Authentication Failed!')
		return value
		
	def create(self, validated_data):
		""" authenticate user
		"""	
		email = validated_data['email']
		password = validated_data['password']
		user = validated_data['user']
		terminal = validated_data['terminal']
		trail = str(self.manager.name)+' '+\
				str(self.manager.email)+' logged in Termial:'+\
				str(terminal)+'. Session active '+str(user)
		user_trail(self.manager,trail,'view')
		return validated_data

class UserTransactionSerializer(serializers.ModelSerializer):
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
		self.l=[]
		user_qs = get_user_model().objects.all()
		for user in user_qs:
			self.l.append(user.email)
		if not email in self.l:		
			raise PermissionDenied('Authentication Failed!')
		else:
			self.user = get_user_model().objects.get(email=email)
		return value

	def validate_password(self,value):
		data = self.get_initial()
		password = data.get('password')
		email = data.get('email')
		if not email in self.l:		
			return value #raise ValidationError('Email does not exist!')
		else:
			self.user = get_user_model().objects.get(email=email)
				
			if self.user.check_password(password):
				self.manager = self.user			
			else:
				raise PermissionDenied('Authentication Failed!')
		return value

	def validate_User(self,value):
		data = self.get_initial()
		user = data.get('User')
		self.user = User.objects.get(pk=int(user))
		return value

	def create(self, validated_data):
		""" authenticate user and transact
		"""			
		manager = self.manager
		terminal = validated_data['terminal']
		amount = validated_data['amount']		
		user = validated_data['User']	
		trans_type = str(validated_data['trans_type'])

		drawer = DrawerCash.objects.create(manager=manager,										   
										   user = User.objects.get(pk=int(user)),
										   terminal=terminal,
										   amount=amount,
										   trans_type=trans_type)
		print drawer		
		return validated_data
		
			
			
		



