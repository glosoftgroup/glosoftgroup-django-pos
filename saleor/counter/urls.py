from django.conf.urls import url
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from .api.views import *
from .models import Counter as Table


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="counter/list.html"), name="index"),
    url(r'^api/create/$', CreateAPIView.as_view(), name='api-create'),
    url(r'^api/delete/(?P<pk>[0-9]+)/$', DestroyView.as_view(), name='api-delete'),
    url(r'^api/list/$', ListAPIView.as_view(), name='api-list'),

    url(r'^api/update/(?P<pk>[0-9]+)/$', UpdateAPIView.as_view(), name='api-update'),
    url(r'^add/$', TemplateView.as_view(template_name="counter/form.html"), name='add'),
    url(r'^update/(?P<pk>[0-9]+)/$', UpdateView.as_view(template_name="counter/form.html", model=Table, fields=['id', 'name']),
        name='update'),
]

