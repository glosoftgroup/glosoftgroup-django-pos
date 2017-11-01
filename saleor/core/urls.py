from django.conf.urls import url

from . import views
from .. import browser_instructions


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^lock/$', views.lock, name='lock'),
    url(r'^lock_process/$', views.lock_process, name='lock_process'),
    url(r'^style-guide/', views.styleguide, name='styleguide'),
    url(r'^not_found/$', views.not_found, name='not_found'),
    url(r'^instructions/(?P<browser>.+)/$', browser_instructions.instructions, name='browser-instructions'),
    url(r'^instructions/$', browser_instructions.instructions, name='browser-instructions2'),
]
