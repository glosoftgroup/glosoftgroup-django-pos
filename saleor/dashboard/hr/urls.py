from django.conf.urls import url

from . import staff_views


urlpatterns = [
    url(r'^$', staff_views.list_staff, name='list-staff'),
    url(r'^detail/(?P<pk>[0-9]+)/$', staff_views.staff_detail, name='staff-detail'),
    url(r'^compose/$', staff_views.add_staff, name='add_staff'),
    url(r'^edit/(?P<pk>[0-9]+)/$', staff_views.staff_edit,
        name='staff-edit'),
    url(r'^delete/(?P<pk>[0-9]+)/$',
        staff_views.staff_delete, name='staff-delete'),
]
