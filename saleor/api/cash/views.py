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
			email = serializer.data['email']
			terminal = serializer.data['terminal']			
			l=[]
			user_qs = get_user_model().objects.all()
			for user in user_qs:
				l.append(user.email)
			if not email in l:		
				return Response({'Authentication Error!'}, status=status.HTTP_400_BAD_REQUEST)
			else:
				user = get_user_model().objects.get(email=email)
				if user.check_password(password) and user.has_perm('sales.make_sale'):					 
					trail = str(user.name)+' '+\
							str(user.email)+' logged in Termial:'+\
							str(terminal)+'. Session active '+str(request.user.name)
					user_trail(user,trail,'view')
				else:
					return Response({'Authentication Error!'}, status=status.HTTP_400_BAD_REQUEST)
			#serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	elif request.method == 'GET':		
			return Response(status=status.HTTP_400_BAD_REQUEST)

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
		user_trail(self.request.user.name,'Drawer Cash:#'+str(serializer.data['amount'])+' added '+str(self.request.user.name),'add')
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

