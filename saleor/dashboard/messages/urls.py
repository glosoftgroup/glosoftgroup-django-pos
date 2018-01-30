from django.conf.urls import url

from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
     url(r'^$', views.list_messages, name='message_list'),
     url(r'^list/(?P<status>[\w\-]+)$', views.list_messages, name='message_list_slug'),
     url(r'^compose/$', views.write, name='compose_message'),
     url(r'^compose/single$', views.write_single, name='compose_single_message'),
     url(r'^contacts/ajax/$', views.contacts, name='message-contacts'),
     url(r'^unread/count/$', views.unread_count, name='unread_count'),
     url(r'^add/template/$', views.add_template, name='add-sms-template'),
     url(r'^get/template/$', views.get_template, name='get-sms-template'),
     url(r'^template/detail/(?P<pk>[0-9]+)$', views.get_template, name='template-detail'),
     url(r'^template/delete/(?P<pk>[0-9]+)$', views.delete_template, name='delete-sms-template'),
     url(r'^read/message/(?P<pk>[0-9]+)$', views.read, name='read-message'),
     url(r'^resend/message/(?P<pk>[0-9]+)$', views.resend, name='resend-message'),
     url(r'^trash/message/(?P<pk>[0-9]+)$', views.delete, name='delete-message'),
     url(r'^delete/permanently/(?P<pk>[0-9]+)$', views.delete_permanently, name='delete-sms-permanently'),
]

if settings.DEBUG:
    # urlpatterns += [ url(r'^static/(?P<path>.*)$', serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)