from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^lock/$', views.lock, name='lock'),
    url(r'^lock_process/$', views.lock_process, name='lock_process'),
    url(r'^style-guide/', views.styleguide, name='styleguide'),
]
