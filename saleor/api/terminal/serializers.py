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
from ...sale.models import Terminal
from ...decorators import user_trail

class TerminalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terminal
        fields = ('id',
                 'terminal_name',
                 'terminal_number')