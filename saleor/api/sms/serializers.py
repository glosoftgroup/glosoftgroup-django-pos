from django.utils.formats import localize
from rest_framework import serializers
from rest_framework.serializers import (
                    SerializerMethodField,
                    ValidationError,
                 )

from django.contrib.auth import get_user_model
from ...smessages.models import SMessage
User = get_user_model()


class MessagesListSerializer(serializers.ModelSerializer):
    sent_to = SerializerMethodField()
    sender = SerializerMethodField()
    date = SerializerMethodField()

    class Meta:
        model = SMessage
        fields = (
                 'id',
                 'sender',
                 'sent_to',
                 'to_number',
                 'verb',
                 'description',
                 'status',
                 'date'
                 )

    def get_sent_to(self, obj):
        try:
            return obj.receipient_details().mobile
        except:
            return ''

    def get_sender(self, obj):
        return obj.actor.name

    def get_date(self, obj):
        return localize(obj.timestamp)


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
    id = serializers.CharField(max_length=30)
    linkId = serializers.CharField(max_length=200)