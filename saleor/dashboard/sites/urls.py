from django.conf.urls import url

from . import views, hr, bank, department

urlpatterns = [
    url(r'^$', views.index, name='site-index'),
    url(r'^(?P<site_id>[0-9]+)/edit/$', views.update, name='site-update'),

    url(r'^hr/$', hr.hr_defaults, name='hr-defaults'),

    url(r'^role/$', hr.add_role, name='add_role'),
    url(r'^redit/(?P<pk>[0-9]+)/$',hr.role_edit, name='role-edit'),
    url(r'^rdelete/(?P<pk>[0-9]+)/$', hr.role_delete, name='role-delete'),

    url(r'^department/$', department.add_department, name='add_department'),
    url(r'^dedit/(?P<pk>[0-9]+)/$', department.department_edit, name='department-edit'),
    url(r'^ddelete/(?P<pk>[0-9]+)/$', department.department_delete, name='department-delete'),

    url(r'^bank/$', bank.add_bank, name='add_bank'),
    url(r'^bedit/(?P<pk>[0-9]+)/$', bank.bank_edit, name='bank-edit'),
    url(r'^bdelete/(?P<pk>[0-9]+)/$', bank.bank_delete, name='bank-delete'),
]
