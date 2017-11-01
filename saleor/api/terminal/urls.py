from django.conf.urls import url

from .views import (
    TerminalListAPIView   
    )


urlpatterns = [
    url(r'^list/$', TerminalListAPIView.as_view(), name='api-terminal-list'),
]

