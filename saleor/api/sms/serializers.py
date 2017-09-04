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
from ...smessages.models import SMessage
from ...decorators import user_trail

class MessagesListSerializer(serializers.ModelSerializer):
	sent_to = SerializerMethodField()
	class Meta:
		model = SMessage
		fields = ('id',
				 'actor', 
				 'sent_to',
				 'verb',
				 'description'
				 )
	def get_sent_to(self,obj):
		return obj.receipient_details().mobile
		

class SmsCallBackSerializer(serializers.Serializer):
	authentication_classes = []
	permission_classes = []
	'''		
    from: The number that sent the message
    to: The number to which the message was sent
    text: The message content
    date: The date and time when the message was received
    id: The internal ID that we use to store this message
    linkId: Optional parameter required when responding to an on-demand user request with a premium message
	'''	
	to = serializers.CharField(max_length=200)
	text = serializers.CharField(max_length=700)
	date = serializers.CharField(max_length=200)
	id   = serializers.CharField(max_length=30)
	linkId = serializers.CharField(max_length=200)