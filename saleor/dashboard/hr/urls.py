from django.conf.urls import url

from . import employees


urlpatterns = [
    url(r'^$', employees.employees, name='employees'),
    url(r'^detail/(?P<pk>[0-9]+)/$', employees.detail, name='employee-detail'),
    url(r'^compose/$', employees.add, name='add_employee'),
    url(r'^eprocess/$', employees.add_process, name='add_employee_process'),
    url(r'^edit/(?P<pk>[0-9]+)/$', employees.edit,
        name='employee-edit'),
    url(r'^delete/(?P<pk>[0-9]+)/$',
        employees.delete, name='employee-delete'),
]
