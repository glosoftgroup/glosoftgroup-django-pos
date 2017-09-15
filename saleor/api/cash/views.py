from django.db.models import Q

from .pagination import PostLimitOffsetPagination, PostPageNumberPagination

from django.contrib.auth import get_user_model
User = get_user_model()

from ...payment.models import MpesaPayment
from .serializers import (
	 UserTransactionSerializer,
	 UserAuthorizationSerializer ,
	 TerminalListSerializer 
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


@api_view(['GET', 'POST'])
def login(request):
	serializer = UserAuthorizationSerializer(data=request.data)
	if request.method == 'POST':		
		if serializer.is_valid():
			password = serializer.data['password']
			username = serializer.data['email']
			try:
				terminal = serializer.data['terminal']		
			except:
				terminal = 'Terminal not set'
			if '@' in username:
				kwargs = {'email': username}
			else:
				kwargs = {'name': username}
			try:
				user = get_user_model().objects.get(**kwargs)
				if user.check_password(password) and user.has_perm('sale.add_drawercash') and user.has_perm('sale.change_drawercash'):
					record_trail(request.user.name,user,terminal)
					return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
				else:
					return Response({'message':'Permission Denied!'}, status=status.HTTP_401_UNAUTHORIZED)
			except:										
				return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)			
		else:
			return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)				
	elif request.method == 'GET':		
			return Response(status=status.HTTP_400_BAD_REQUEST)

def record_trail(loggedin,user,terminal):
	trail = str(user.name)+' '+\
			str(user.email)+' logged in Termial:'+\
			str(terminal)+'. Session active '+str(loggedin)
	user_trail(user,trail,'view')

@api_view(['GET', 'POST'])
def logout(request):
	auth.logout(request)
	return Response({
		'users': "User logged out successfully"})


class UserAuthorizationAPIView(generics.CreateAPIView):
	"""docstring for UserAuthorizationAPIView"""
	serializer_class = UserAuthorizationSerializer
		
class UserTransactionAPIView(generics.CreateAPIView,):    
	serializer_class = UserTransactionSerializer
	def perform_create(self, serializer):              
		serializer.save(user=self.request.user)
		user_trail(self.request.user,'Drawer Cash:#'+str(serializer.data['amount'])+' added ','add')
		info_logger.info('User: '+str(self.request.user)+' Drawer Cash:'+str(serializer.data['amount']))

class TerminalListAPIView(generics.ListAPIView):
    pagination_class = PostLimitOffsetPagination
    serializer_class = TerminalListSerializer

    def get_queryset(self, *args, **kwargs):        
        queryset_list = Terminal.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(terminal_name__icontains=query)|
                Q(terminal_number__icontains=query)               
                ).order_by('-id')
        return queryset_list

