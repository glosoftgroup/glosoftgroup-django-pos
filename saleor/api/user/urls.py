from django.conf.urls import url

from .views import (
    UserListAPIView
    )


urlpatterns = [
    url(r'^$', UserListAPIView.as_view(), name='api-users-list'),
]

