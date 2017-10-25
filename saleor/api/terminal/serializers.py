from rest_framework import serializers
from ...sale.models import Terminal


class TerminalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terminal
        fields = (
                 'id',
                 'terminal_name',
                 'terminal_number')