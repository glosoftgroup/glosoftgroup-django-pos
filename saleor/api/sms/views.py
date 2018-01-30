from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import pagination

from ...smessages.models import SMessage as Notification
from .pagination import PostLimitOffsetPagination
from .serializers import (
     SmsCallBackSerializer,
     MessagesListSerializer,
     )
from ...decorators import user_trail
import logging

User = get_user_model()
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


class MessagesListAPIView(generics.ListAPIView):
    serializer_class = MessagesListSerializer
    pagination_class = PostLimitOffsetPagination

    def get_serializer_context(self):
        if self.request.GET.get('date'):
            return {"date": self.request.GET.get('date'), 'request': self.request}
        return {"date": None, 'request': self.request}

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs['pk']:
                queryset_list = Notification.objects.filter(user__pk=self.kwargs['pk']).select_related()
            else:
                queryset_list = Notification.objects.all.select_related()
        except Exception as e:
            queryset_list = Notification.objects.all()
            query = self.request.GET.get('q')
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('status'):
            if self.request.GET.get('status') == 'all':
                pass
            elif self.request.GET.get('status') == 'Success':
                queryset_list = queryset_list.filter(status=self.request.GET.get('status'))
            else:
                queryset_list = queryset_list.exclude(status='Success')
        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(timestamp__icontains=self.request.GET.get('date'))
        if query:
            queryset_list = queryset_list.filter(
                Q(verb__icontains=query) |
                Q(description__icontains=query) |
                Q(to_number__icontains=query)
                )
        return queryset_list.order_by('-id')


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

