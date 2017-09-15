from django.db.models import Q

from .pagination import PostLimitOffsetPagination, PostPageNumberPagination

from django.contrib.auth import get_user_model
User = get_user_model()

from ...payment.models import MpesaPayment
from ...smessages.models import SMessage as Notification

from .serializers import (
     SmsCallBackSerializer,
     MessagesListSerializer ,    
     )
from rest_framework import generics 
from rest_framework.response import Response
from django.contrib import auth
from ...decorators import user_trail
from ...sale.models import Terminal
import logging
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')     
from rest_framework.decorators import api_view
from rest_framework import status
from ...smessages.models import SMessage
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt, csrf_protect


class MessagesListAPIView(generics.ListAPIView):
    queryset = SMessage.objects.all()
    serializer_class = MessagesListSerializer


#@csrf_exempt
class callback(APIView):
    '''     
    from: The number that sent the message
    to: The number to which the message was sent
    text: The message content
    date: The date and time when the message was received
    id: The internal ID that we use to store this message
    linkId: Optional parameter required when responding to an on-demand user request with a premium message
    '''
    authentication_classes =[]
    permission_classes = []    

    def post(self, request, format=None):
        serializer = SmsCallBackSerializer(data=request.data)
        if serializer.is_valid():
            actor = User.objects.all().first()
            sender = request.POST.get('from')
            to = serializer.data['to']
            text = serializer.data['text']      
            date = serializer.data['date']
            id = serializer.data['id']
            linkId = serializer.data['linkId']
            notif = Notification.objects.create(
                            to='anonymous', 
                            actor=actor, 
                            recipient=actor,
                            from_number=sender,
                            to_number=to,
                            external_id=id,
                            link_id=linkId, 
                            #sent_to=user.id,  
                            verb=text,
                            sent=True, 
                            description=text,
                            status='success')
            print notif.status
            return Response({'message':sender},status=status.HTTP_201_CREATED)          
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['GET', 'POST'])
def callbackgg(request):
    authentication_classes = []
    permission_classes = []
    '''     
    from: The number that sent the message
    to: The number to which the message was sent
    text: The message content
    date: The date and time when the message was received
    id: The internal ID that we use to store this message
    linkId: Optional parameter required when responding to an on-demand user request with a premium message
    '''
    actor = User.objects.all().first()
    serializer = SmsCallBackSerializer(data=request.data)
    if request.method == 'POST':        
        if serializer.is_valid():
            sender = request.POST.get('from')
            to = serializer.data['to']
            text = serializer.data['text']      
            date = serializer.data['date']
            id = serializer.data['id']
            linkId = serializer.data['linkId']
            notif = Notification.objects.create(
                            to='anonymous', 
                            actor=actor, 
                            recipient=actor,
                            from_number=sender,
                            to_number=to,
                            external_id=id,
                            link_id=linkId, 
                            #sent_to=user.id,  
                            verb=text,
                            sent=True, 
                            description=text,
                            status='success')
            print notif.status
            return Response({'message':sender},status=status.HTTP_201_CREATED)          
        return Response({'message','error'},status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':       
            return Response({'message':'invalid method GET'},status=status.HTTP_400_BAD_REQUEST)

def record_trail(loggedin,user,terminal):
    trail = str(user.name)+' '+\
            str(user.email)+' logged in Termial:'+\
            str(terminal)+'. Session active '+str(loggedin)
    user_trail(user,trail,'view')

