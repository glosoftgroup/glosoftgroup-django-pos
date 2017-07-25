from django.conf.urls import url

from . import views, hr, bank, department, branch

urlpatterns = [
    url(r'^$', views.index, name='site-index'),
    url(r'^(?P<site_id>[0-9]+)/edit/$', views.update, name='site-update'),

    url(r'^hr/$', hr.hr_defaults, name='hr-defaults'),

    url(r'^role/$', hr.add_role, name='add_role'),
    url(r'^redit/(?P<pk>[0-9]+)/$',hr.role_edit, name='role-edit'),
    url(r'^rdelete/(?P<pk>[0-9]+)/$', hr.role_delete, name='role-delete'),
    url(r'^view/roles/$', hr.view_roles, name='view_roles'),
    url(r'^roles/paginate/$', hr.roles_paginate, name='roles_paginate'),
    url(r'^roles/search/$', hr.search, name='roles_search'),

    url(r'^department/$', department.add_department, name='add_department'),
    url(r'^dedit/(?P<pk>[0-9]+)/$', department.department_edit, name='department-edit'),
    url(r'^ddelete/(?P<pk>[0-9]+)/$', department.department_delete, name='department-delete'),
    url(r'^view/depar/$', department.view_department, name='view_department'),
    url(r'^department/paginate/$', department.department_paginate, name='department_paginate'),
    url( r'^department/search/$', department.search, name = 'department_search' ),

    url(r'^bank/$', bank.add_bank, name='add_bank'),
    url(r'^bedit/(?P<pk>[0-9]+)/$', bank.bank_edit, name='bank-edit'),
    url(r'^bdelete/(?P<pk>[0-9]+)/$', bank.bank_delete, name='bank-delete'),
    url(r'^view/$', bank.view_bank, name='view_bank'),
    url(r'^bank/paginate/$', bank.bank_paginate, name='bank_paginate'),
    url( r'^bank/search/$', bank.search, name = 'bank_search' ),

    url(r'^bank/branches/(?P<pk>[0-9]+)/$', branch.view, name='bank_branches'),
    url(r'^branch/$', branch.add_branch, name='add_branch'),
    url(r'^bredit/(?P<pk>[0-9]+)/$', branch.branch_edit, name='branch-edit'),
    url(r'^brdelete/(?P<pk>[0-9]+)/$', branch.branch_delete, name='branch-delete'),
    url(r'^branch/paginate/$', branch.branch_paginate, name='branch_paginate'),
    url( r'^branch/search/$', branch.search, name = 'branch_search' ),
]
