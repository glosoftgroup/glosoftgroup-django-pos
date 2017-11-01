from ...site.models import SiteSettings
from .serializers import (
    SiteSettingSerializer,
     )
from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly
User = get_user_model()


class SiteSettingListAPIView(generics.ListAPIView):
    """
        list site settings details
        GET /api/setting/
    """
    serializer_class = SiteSettingSerializer
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = SiteSettings.objects.all()


