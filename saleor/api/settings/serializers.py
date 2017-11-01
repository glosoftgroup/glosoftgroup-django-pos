# site settings rest api serializers

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...site.models import SiteSettings
User = get_user_model()


class SiteSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ('id',
                  'name',
                  'image',
                 )

