from django.conf.urls import url

from .views import (
    UserTransactionAPIView,  
    UserAuthorizationAPIView,
    )


urlpatterns = [
    url(r'^$', 
    	UserTransactionAPIView.as_view(),
    	name='transaction'), 
    url(r'^auth/',
    	UserAuthorizationAPIView.as_view(),
    	name='authorization'),   
    
]

