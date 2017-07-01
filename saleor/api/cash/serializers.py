# Payment rest api serializers
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
from ...sale.models import DrawerCash, Terminal
from ...decorators import user_trail


class UserAuthorizationSerializer(serializers.Serializer):
	email = serializers.EmailField()
	password = serializers.CharField(max_length=200)
	user = serializers.CharField(max_length=200)
	terminal = serializers.CharField(max_length=200)

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

	def validate_terminal(self,value):
		data = self.get_initial()
		self.terminal_id = int(data.get('terminal'))
		self.l=[]
		terminals = Terminal.objects.all()
		for term in terminals:
			self.l.append(term.pk)
		if not self.terminal_id in self.l:		
			raise ValidationError('Terminal specified does not extist')
		return value
	
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

	def validate_amount(self,value):
		data = self.get_initial()
		terminal = int(data.get('terminal'))
		self.amount = Decimal(data.get('amount'))
		return value

	def validate_trans_type(self,value):	
		data = self.get_initial()
		self.type = str(data.get('trans_type'))
		if self.type != 'deposit' and self.type != 'withdraw':
			raise PermissionDenied('Transaction type error!')
		return value

		
	def create(self, validated_data):
		""" authenticate user and transact
		"""
		trans_type = str(validated_data['trans_type'])
		amount = validated_data['amount']	
		terminal = Terminal.objects.get(pk=self.terminal_id)	
		if trans_type == 'deposit':
			terminal.amount += Decimal(amount)			
			terminal.save()
		elif trans_type == 'withdraw':
			print 'pending....'
			

		manager = self.manager
		terminal = validated_data['terminal']				
		user = validated_data['User']	

		drawer = DrawerCash.objects.create(manager=manager,										   
										   user = User.objects.get(pk=int(user)),
										   terminal=terminal,
										   amount=amount,
										   trans_type=trans_type)
		print drawer		
		return validated_data
		
			
			
		



