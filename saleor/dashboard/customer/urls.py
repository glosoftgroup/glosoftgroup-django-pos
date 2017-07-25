from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
        url(r'^$', views.users, name='customers'),        
        url(r'^add/$', permission_required('userprofile.add_user', login_url='account_login')
            (views.user_add), name='customer-add'),
        url(r'^customer_process/$', views.user_process, name='customer_process'),
        url(r'^detail/(?P<pk>[0-9]+)/$', views.user_detail, name='customer-detail'),
        url(r'^delete/(?P<pk>[0-9]+)/$', views.user_delete, name='customer-delete'),
        url(r'^edit/(?P<pk>[0-9]+)/$', views.user_edit, name='customer-edit'),
        url(r'^user_update(?P<pk>[0-9]+)/$', views.user_update, name='customer-update'),
        # url(r'^add/', permission_required('userprofile.add_user', login_url='account_login')(views.user_add)),
        
]

if settings.DEBUG:
    # urlpatterns += [ url(r'^static/(?P<path>.*)$', serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)