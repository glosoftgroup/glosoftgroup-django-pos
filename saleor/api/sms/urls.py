from django.conf.urls import url

from .views import (
    MessagesListAPIView,  
    callback,   
    )


urlpatterns = [
    url(r'^$', 
    	callback.as_view(),
    	name='message-callback-url'), 
    url(r'^list/messages/',
    	MessagesListAPIView.as_view(),
    	name='list-messages'),    
]

