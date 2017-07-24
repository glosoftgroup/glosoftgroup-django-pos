from django.conf.urls import url

from . import employees, attendance


urlpatterns = [
    url(r'^$', employees.employees, name='employees'),
    url(r'^detail/(?P<pk>[0-9]+)/$', employees.detail, name='employee-detail'),
    url(r'^compose/$', employees.add, name='add_employee'),
    url(r'^eprocess/$', employees.add_process, name='add_employee_process'),
    url(r'^edit/(?P<pk>[0-9]+)/$', employees.edit, name='employee-edit'),
    url(r'^delete/(?P<pk>[0-9]+)/$', employees.delete, name='employee-delete'),
    url( r'^employees/search/$', employees.search, name = 'employees_search' ),
    url(r'^employees/paginate/', employees.paginate, name='employees_paginate'),

    url(r'^attendance/$', attendance.attendance, name='attendance'),
    url(r'^a/detail/(?P<pk>[0-9]+)/$', attendance.detail, name='attendance-detail'),
    url(r'^fill/$', attendance.add, name='add_attendance'),
    url(r'^a/process/$', attendance.add_process, name='add_attendance_process'),
]
