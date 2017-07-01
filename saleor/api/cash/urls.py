from django.conf.urls import url

from .views import (
    UserTransactionAPIView,  
    UserAuthorizationAPIView,
    logout,
    login,
    )


urlpatterns = [
    url(r'^$', 
    	UserTransactionAPIView.as_view(),
    	name='transaction'), 
    url(r'^auth/',
    	UserAuthorizationAPIView.as_view(),
    	name='authorization'),
    url(r'^login/',login, name='login'),
    url(r'^logout/',logout, name='logout'),  
    
]

