from django.conf.urls import url

from .views import (    
    AllocateCreateAPIView,
    AllocateListAPIView,
    AllocateUpdateAPIView,
    )


urlpatterns = [
    url(r'^$', AllocateListAPIView.as_view(),
     name='list-allocate'),
    url(r'^search-allocate/$', AllocateListAPIView.as_view(),
     name='search-allocate'),
    url(r'^update-allocate/(?P<pk>[0-9]+)/$', AllocateUpdateAPIView.as_view(),
     name='update-allocate'),
    url(r'^create-allocate/$',
        AllocateCreateAPIView.as_view(), name='create-allocate'),
    
]

