from django.conf.urls import url

from .views import (
    AllocateAgentListAPIView,
    AllocateCreateAPIView,
    AllocateListAPIView,
    AllocateUpdateAPIView,
    CarListAPIView
    )


urlpatterns = [
    url(r'^$', AllocateListAPIView.as_view(), name='list-allocate'),
    url(r'^car$', CarListAPIView.as_view(), name='api-car-report-list'),
    url(r'^search/$', AllocateListAPIView.as_view(), name='search-allocate'),
    url(r'^agent/(?P<pk>[0-9]+)/$', AllocateAgentListAPIView.as_view(),
        name='search-agent-allocate'),
    url(r'^update/(?P<pk>[0-9]+)/$', AllocateUpdateAPIView.as_view(),
     name='update-allocate'),
    url(r'^create/$',
        AllocateCreateAPIView.as_view(), name='create-allocate'),
    
]

