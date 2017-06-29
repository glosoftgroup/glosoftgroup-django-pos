from django.conf.urls import url

from .views import (
    UserAuthenticationAPIView,  
    )


urlpatterns = [
    url(r'^$', 
    	UserAuthenticationAPIView.as_view(),
    	name='authenticate'),    
    
]

