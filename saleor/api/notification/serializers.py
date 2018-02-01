from rest_framework import serializers
from rest_framework.serializers import (
                    SerializerMethodField,
                    ValidationError,
                 )

from django.contrib.auth import get_user_model
from django.utils.dateformat import DateFormat
from notifications.models import Notification as SMessage
User = get_user_model()


class MessagesListSerializer(serializers.ModelSerializer):
    sent_to = SerializerMethodField()
    sender = SerializerMethodField()
    recipient_name = SerializerMethodField()
    date = SerializerMethodField()
    status = SerializerMethodField()
    read_url = serializers.HyperlinkedIdentityField(view_name='dashboard:read-notification')

    class Meta:
        model = SMessage
        fields = (
                 'id',
                 'sender',
                 'sent_to',
                 'recipient_name',
                 'verb',
                 'description',
                 'date',
                 'status',
                 'read_url'
                 )

    def get_recipient_name(self, obj):
        try:
            return obj.recipient.name
        except:
            return ''

    def get_sent_to(self, obj):
        try:
            return obj.receipient_details().mobile
        except:
            return ''

    def get_sender(self, obj):
        return obj.actor.name

    def get_date(self, obj):
        return DateFormat(obj.timestamp).format('Y-m-d')

    def get_status(self, obj):
        if obj.unread:
            return '<i class="icon-mail5 text-success" > </i>'
        else:
            return '<i class ="icon-mail-read text-muted"> </i>'

