from django.conf.urls import url

from .views import (
    SiteSettingListAPIView,
    )


urlpatterns = [
    url(r'^$', SiteSettingListAPIView.as_view(),
        name='api-site_settings-list'),
]

