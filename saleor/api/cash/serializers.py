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
from ...sale.models import DrawerCash, Terminal, TerminalHistoryEntry
from ...decorators import user_trail

class TerminalListSerializer(serializers.ModelSerializer):
	todaySales = SerializerMethodField()
	class Meta:
		model = Terminal
		fields = ('id',
				 'terminal_name',
				 'terminal_number',
				 'amount',
				 'todaySales'
				 )
	def get_todaySales(self,obj):
		return obj.get_todaySales()

class UserAuthorizationSerializer(serializers.Serializer):
	email = serializers.CharField()
	password = serializers.CharField(max_length=200)
	user = serializers.CharField(max_length=200)
	terminal = serializers.CharField(max_length=200,allow_blank=True,required=False)

	def validate_user(self,value):
		data = self.get_initial()
		user = data.get('user')
		try:
			self.user = User.objects.get(pk=int(user))
			return value
		except:
			raise ValidationError('User does not exist')

	def validate_terminal(self,value):
		data = self.get_initial()
		try:
			Terminal.objects.get(pk=int(data.get('terminal')))
		except:
			raise ValidationError('Terminal specified does not extist')
		return value

class UserTransactionSerializer(serializers.ModelSerializer):
	email = serializers.CharField(max_length=200)
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
				  'trans_type',
				  'note')

	def validate_terminal(self,value):
		data = self.get_initial()
		try:
			terminal = Terminal.objects.get(pk=int(data.get('terminal')))
			if terminal:
				self.terminal = terminal
				return value
			else:
				raise ValidationError('Terminal specified does not extist')
		except:
			raise ValidationError('Terminal specified does not extist')
		return value

	def validate_note(self, value):
		data = self.get_initial()
		try:
		  if data.get('note'):
		  	 return value
		  else:
		  	raise ValidationError('Add a note!')
		except:
			raise ValidationError('Add a note!')


	def validate_email(self, value):
		data = self.get_initial()
		username = data.get('email')
		if '@' in username:
			kwargs = {'email': username}
		else:
			kwargs = {'name': username}
		try:
			user = get_user_model().objects.get(**kwargs)
			if not user:
				raise PermissionDenied('Username/email error Authentication Failed!')
			else:
				return value
		except:
			raise PermissionDenied('Username/email Failed!')
		return value

	def validate_password(self,value):
		data = self.get_initial()
		password = data.get('password')
		username = data.get('email')
		if '@' in username:
			kwargs = {'email': username}
		else:
			kwargs = {'name': username}
		try:
			user = get_user_model().objects.get(**kwargs)
			if user.check_password(password) and user.has_perm('sale.add_drawercash') and user.has_perm('sale.change_drawercash'):
				self.manager = user
				return value
			else:
				raise PermissionDenied('Authentication Failed!')
		except:
			raise PermissionDenied('Authentication Failed!')
		return value

	def validate_User(self,value):
		data = self.get_initial()
		try:
			user = User.objects.get(pk=int(data.get('User')))
			if not user:
				raise PermissionDenied('Cashier Authentication Failed!')
			else:
				return value
		except:
			raise ValidationError('Cashier does not extist')
		return value



	def validate_trans_type(self,value):
		data = self.get_initial()
		trans_type = str(data.get('trans_type'))
		if trans_type != 'deposit' and self.type != 'withdraw':
			raise ValidationError('Transaction type error!')
		return value

	def validate_amount(self,value):
		data = self.get_initial()
		try:
			terminal_id = int(data.get('terminal'))
		except:
			raise ValidationError('Terminal id required!')
		self.amount = Decimal(data.get('amount'))
		self.type = str(data.get('trans_type'))
		if self.type != 'deposit' and self.type != 'withdraw':
			raise ValidationError('Transaction type error!')
		if self.type == 'withdraw':
			self.terminal = Terminal.objects.get(pk=terminal_id)
			if self.terminal.amount < self.amount:
				raise ValidationError('Insufficient cash in drawer!')
		return value


	def create(self, validated_data):
		""" authenticate user and transact
		"""
		trans_type = str(validated_data['trans_type'])
		amount = validated_data['amount']
		manager = self.manager
		terminal = validated_data['terminal']
		user = validated_data['User']
		note = validated_data['note']

		trail = str(manager)+' '+trans_type+' '+str(amount)+\
					' from TERMINAL:'+str(terminal)
		print trail
		if trans_type == 'deposit':
			self.terminal.amount += Decimal(amount)
			self.terminal.save()
			TerminalHistoryEntry.objects.create(
							terminal=terminal,
							comment=trail,
							crud=trans_type,
							user=manager
						)
		elif trans_type == 'withdraw':
			self.terminal.amount -= Decimal(amount)
			self.terminal.save()
			TerminalHistoryEntry.objects.create(
							terminal=terminal,
							comment=trail,
							crud=trans_type,
							user=manager
						)


		drawer = DrawerCash.objects.create(manager=manager,
										   user = User.objects.get(pk=int(user)),
										   terminal=terminal,
										   amount=amount,
										   trans_type=trans_type,
										   note=note)
		print drawer

		return validated_data



