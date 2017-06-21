from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from .userprofile.models import UserTrail
from django.shortcuts import get_object_or_404
from datetime import date
from django.utils import timezone
import logging

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

def permission_decorator(argument):
	def permitted_users_only(function):
		def wrap(request, *args, **kwargs):
			if request.user.has_perm(argument):
				info_logger.info('status: 200, '+ str(argument)+' permission granted for '+str(request.user))
				return function(request, *args, **kwargs)
			else:
				debug_logger.debug('status: 403, '+ str(argument)+' permission denied for '+str(request.user))				
				return HttpResponse('permission denied')
		return wrap
	return permitted_users_only

def user_trail(name, action, tag=None):
	# try:
	# 	record = UserTrail(name=name, action=action)
	# 	record.save()
	# 	info_logger.info(str(name)+' - '+str(action))
	# except:
	# 	HttpResponse('error saving action')
	# 	info_logger.info('status: 400, not able to add action')
	record = UserTrail(name=name, action=action, crud= tag, date=date.today())
	record.save()
