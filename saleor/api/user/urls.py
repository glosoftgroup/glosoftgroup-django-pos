from django.conf.urls import url

from .views import (
    AgentListAPIView,
    UserListAPIView
    )


urlpatterns = [
    url(r'^$', UserListAPIView.as_view(), name='api-users-list'),
    url(r'^agent/$', UserListAPIView.as_view(), name='api-agent-list'),
]

