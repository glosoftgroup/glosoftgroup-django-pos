from django.conf.urls import url

from . import views, hr

urlpatterns = [
    url(r'^$', views.index, name='site-index'),
    url(r'^(?P<site_id>[0-9]+)/edit/$', views.update, name='site-update'),

    url(r'^hr/$', hr.hr_defaults, name='hr-defaults'),
    url(r'^role/$', hr.add_role, name='add_role'),
]
