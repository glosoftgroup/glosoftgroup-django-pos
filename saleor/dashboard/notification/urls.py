from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
     url(r'^$', views.notification_list, name='notification_list'),
     url(r'^list/(?P<status>[\w\-]+)$', views.notification_list, name='notification_list_slug'),
     url(r'^write/$', views.write, name='write'),
     url(r'^unread/count/$', views.unread_count, name='unread_count'),
     url(r'^read/notification/(?P<pk>[0-9]+)$', views.read, name='read-notification'),
     url(r'^emails/ajax/$', views.emails, name='notification-emails'),
     url(r'^delete/notification/(?P<pk>[0-9]+)$', views.delete, name='delete-notification'),
     url(r'^delete/permanently/(?P<pk>[0-9]+)$', views.delete_permanently, name='delete-permanently'),
     # templates
     url(r'^add/template/$', views.add_template, name='add-email-template'),
     url(r'^get/template/$', views.get_template, name='get-email-template'),
     url(r'^template/detail/(?P<pk>[0-9]+)$', views.get_template, name='email-template-detail'),
     url(r'^template/delete/(?P<pk>[0-9]+)$', views.delete_template, name='delete-email-template'),
     
]

if settings.DEBUG:
    # urlpatterns += [ url(r'^static/(?P<path>.*)$', serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)