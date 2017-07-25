from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.list_messages, name='list-messages'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.message_detail, name='message-detail'),
    url(r'^compose/$', views.compose, name='compose'),
]
