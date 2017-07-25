from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
        url(r'^$', permission_required('userprofile.view_user', login_url='not_found')
                (views.users), name='users'),
        url(r'^add/$', permission_required('userprofile.add_user', login_url='not_found')
                (views.user_add), name='user-add'),
        url(r'^users_pdf/$', views.users_pdf, name='users_pdf'),
        url(r'^users_export_csv/$', views.users_export_csv, name='users_export_csv'),
        url(r'^user_process/$',  permission_required('userprofile.add_user')
        (views.user_process), name='user_process'),
        url(r'^detail/(?P<pk>[0-9]+)/$', permission_required('userprofile.change_user', login_url='not_found')(views.user_detail), name='user-detail'),
        url(r'user_trail/$', permission_required('unused.view_trail', login_url='not_found')
                (views.user_trails), name='user_trail'),
        url(r'^usertrail_paginate/', views.usertrail_paginate, name='usertrail_paginate'),
        url( r'^usertrail_search/$', views.usertrail_search, name = 'usertrail_search' ),
        url(r'^delete/(?P<pk>[0-9]+)/$', permission_required('userprofile.delete_user')
                (views.user_delete), name='user-delete'),
    
        url(r'^edit/(?P<pk>[0-9]+)/$', permission_required('userprofile.change_user', login_url='not_found')(views.user_edit), name='user-edit'),
        url(r'^user_update(?P<pk>[0-9]+)/$', permission_required('userprofile.change_user', login_url='not_found')
                (views.user_update), name='user-update'),
        url(r'^user_assign_permission/$', views.user_assign_permission, name='user_assign_permission'),
        url(r'^user_paginate/', views.user_paginate, name='user_paginate'),
        url( r'^users_search/$', views.user_search, name = 'user_search' ),
        
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)