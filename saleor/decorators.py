from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from .userprofile.models import UserTrail
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from django.utils import timezone
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
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
				raise PermissionDenied()
		return wrap
	return permitted_users_only

def user_trail(name, action, tag=None):
	record = UserTrail(name=name, action=action, crud= tag, date=date.today())
	record.save()


class EmailOrUsernameModelBackend(object):
	"""
	This is a ModelBacked that allows authentication with either a username or an email address.

	"""
	def authenticate(self, username=None, password=None):
		username = username.lower()
		if '@' in username:
			kwargs = {'email': username}
		else:
			kwargs = {'name': username}
		try:
			user = get_user_model().objects.get(**kwargs)
			if user.check_password(password):
				return user
		except ObjectDoesNotExist:
			return None

	def get_user(self, username):
		try:
			return get_user_model().objects.get(pk=username)
		except get_user_model().DoesNotExist:
			return None