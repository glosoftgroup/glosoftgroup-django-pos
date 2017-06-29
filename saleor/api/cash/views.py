from django.db.models import Q

from .pagination import PostLimitOffsetPagination, PostPageNumberPagination

from django.contrib.auth import get_user_model
User = get_user_model()

from ...payment.models import MpesaPayment
from .serializers import (
     UserAuthenticationSerializer  
     )
from rest_framework import generics 
from ...decorators import user_trail
import logging
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')     


class UserAuthenticationAPIView(generics.CreateAPIView,):    
    serializer_class = UserAuthenticationSerializer
    def perform_create(self, serializer):              
        serializer.save(amount=90,user=self.request.user)
        user_trail(self.request.user.name,'Drawer Cash:#'+str(serializer.data['amount'])+' added '+str(self.request.user.name),'add')
        info_logger.info('User: '+str(self.request.user)+' Drawer Cash:'+str(serializer.data['amount']))



