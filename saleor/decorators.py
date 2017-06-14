from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from .userprofile.models import UserTrail
from django.shortcuts import get_object_or_404
import logging
from .api.product.serializers import UserSerializer

def jwt_response_payload_handler(token, user=None, request=None):
        return {
            'token': token,
            'user': UserSerializer(user, context={'request': request}).data
        }

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

def permission_decorator(argument):
	def permitted_users_only(function):
		def wrap(request, *args, **kwargs):
			if request.user.has_perm(argument):
				debug_logger.debug('status: 200, access granted for '+str(request.user))
				return function(request, *args, **kwargs)
			else:
				debug_logger.debug('status: 403, permission denied for '+str(request.user))
				return HttpResponse('permission denied')
		return wrap
	return permitted_users_only

def user_trail(name, action):
	# try:
	# 	record = UserTrail(name=name, action=action)
	# 	record.save()
	# 	info_logger.info(str(name)+' - '+str(action))
	# except:
	# 	HttpResponse('error saving action')
	# 	info_logger.info('status: 400, not able to add action')
		record = UserTrail(name=name, action=action)
		record.save()
