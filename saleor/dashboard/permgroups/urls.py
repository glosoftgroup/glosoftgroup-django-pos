from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
        url(r'^$', permission_required('auth.view_group', login_url='not_found')
                (views.groups), name='groups'),
        url(r'^groups/$', views.perms, name='perms'),
        url(r'^add_group/$', permission_required('auth.add_group', login_url='not_found')
                (views.create_group), name='add_group'),
        url(r'^group_assign_permission/$', permission_required('auth.add_group', login_url='not_found')
                (views.group_assign_permission), name='group_assign_permission'),
        url(r'^get_search_users/$', views.get_search_users, name='get_search_users'),
        url(r'^group_edit/$', permission_required('auth.change_group', login_url='not_found')
                (views.group_edit), name='group_edit'),
        url(r'^group_manage/$', views.group_manage, name='group_manage'),
        url(r'^get_group_users/$', views.get_group_users, name='get_group_users'),
        url(r'^group_update/$', permission_required('auth.change_group', login_url='home')
                (views.group_update), name='group_update'),
        url(r'^detail/(?P<pk>[0-9]+)/$', permission_required('auth.view_group', login_url='not_found')
                (views.group_detail), name='group-detail'),
        url(r'^delete/(?P<pk>[0-9]+)/$', permission_required('auth.delete_group', login_url='not_found')
                (views.group_delete), name='group-delete'),
        url(r'^group_paginate/', views.group_paginate, name='group_paginate'),
        url( r'^groups_search/$', views.group_search, name = 'group_search' ),
        
]

if settings.DEBUG:
    # urlpatterns += [ url(r'^static/(?P<path>.*)$', serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)