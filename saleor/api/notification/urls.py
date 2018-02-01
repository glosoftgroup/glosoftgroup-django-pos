from django.conf.urls import url

from .views import (
    MessagesListAPIView
)


urlpatterns = [
    url(r'^list/messages/', MessagesListAPIView.as_view(), name='list-messages'),
]

