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
     url(r'^read/notifiction/(?P<pk>[0-9]+)$', views.read, name='read-notification'),
     url(r'^delete/notifiction/(?P<pk>[0-9]+)$', views.delete, name='delete-notification'),
]

if settings.DEBUG:
    # urlpatterns += [ url(r'^static/(?P<path>.*)$', serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)